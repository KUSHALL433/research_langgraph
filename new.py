from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph,START,END,add_messages
from typing import TypedDict,Annotated
from langchain_core.messages import SystemMessage,BaseMessage,HumanMessage
from dotenv import load_dotenv
from langchain_core.tools import tool
from pypdf import PdfReader
import requests
from io import BytesIO
import trafilatura


load_dotenv()
model=ChatGroq(model="groq/compound")

search_tool=TavilySearch()

@tool
def get_text_data(url:str):
    """This tool takes as input tavily-search results URL and extracts text from that PDF or URL link"""
    extracted_text=""
    if url.endswith(".pdf"):
        try:
            response = requests.get(url)
            response.raise_for_status()

            pdf_file = BytesIO(response.content)
            reader = PdfReader(pdf_file)
            pdf_text = f"\n\n".join(
                reader.pages[i].extract_text() for i in range(len(reader.pages))
                )
            extracted_text=f"\n\n{pdf_text}"
        except Exception as e:
                extracted_text=f"\n\nError extracting PDF:{e}"

    else:
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                website_text = f"\n\n" + trafilatura.extract(downloaded)
                extracted_text=f"\n\n{website_text}"
            else:
                extracted_text = f"\n\nCould not extract text from this site"
        except Exception as e:
                extracted_text=f"\n\nError extracting website: {e}"
    return extracted_text


class AgentState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    url_list:list[str]
    extracted_text:str
    summary:str


def chat_search_tool(state: AgentState):
    url_list=[]
    output=search_tool.invoke(state['messages'][0].content)
    output=output['results']
    for dict in output:
        url_list.append(dict['url'])

    return {'url_list':url_list}


def chat_extracted_text(state:AgentState):
    url_list=state['url_list']
    extract_text=""
    for url in url_list:
        extract_text+=get_text_data.invoke(url)

    return {"extracted_text":extract_text}



def generate_summary(state:AgentState):
    system_content = f"""You are a helpful research assistant that generates a structured report on the given extracted text. The report follows the following report format.
    Report:
    Title- **Suitable title based on context**
    Summary- ** A nice summary of the text **
    Key findings- ** Key findings from report **
    Conclusion- ** A unique conclusion on report **

    The length of report should be minimum 100 words and maximum 500 words.
    """
    
    user_content = f"""Context/ Extracted-Text:
    {state['extracted_text'][:5000]}
    
    Based on the context provided above, generate the complete structured report.
    """

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_content) 
    ]
    
    summary = model.invoke(messages).content
    return {'summary':summary}


graph = StateGraph(AgentState)

graph.add_node("search_tool", chat_search_tool)
graph.add_node("text_extraction_tool", chat_extracted_text)
graph.add_node("summarize", generate_summary)


graph.add_edge(START, "search_tool")
graph.add_edge("search_tool","text_extraction_tool")
graph.add_edge("text_extraction_tool", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()
app
output=app.invoke({'messages':[HumanMessage(content="Impact of AI on education")],'extracted_text':"",'summary':"",'url_list':[]})

print(output['summary'])

