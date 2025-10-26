import streamlit as st
from new import app
from langchain_core.messages import HumanMessage
from db import create_table, fetch_reports, fetch_report_details

create_table()

st.set_page_config(page_title="Researchy | LangGraph based topic researcher and report generator.",page_icon="✍🏻")

st.info(
    body="This a LangGraph based topic Research Agent that generates a structured report on given topic.",
    icon="ℹ️"
)

st.title("Welcome !",anchor=False)

st.sidebar.title("📁 Previous Reports")
reports = fetch_reports()

if reports:
    selected = st.sidebar.selectbox(
        "Select report:", reports,
        format_func=lambda x: f"{x[1]} ({str(x[2])[:10]})"
    )
    if selected:
        topic, urls, report_text = fetch_report_details(selected[0])
        st.sidebar.write(f"**Topic:** {topic}")
else:
    st.sidebar.write("No reports yet.")

user_query=st.text_input("Enter a topic.",placeholder="Example: Impact of AI on Education.")

if st.button("Submit"):
    if not user_query.strip():
        st.warning("⚠️ Please enter a valid topic.")
    else:
        with st.spinner("🔍 Researching and generating report..."):
            try:
                result = app.invoke({
                    'messages': [HumanMessage(content=user_query)],
                    'extracted_text': "",
                    'summary': "",
                    'url_list': []
                })
                st.success("✅ Report Successfully Generated!")
                st.subheader("📄 Generated Report:",anchor=False)
                st.write(result['summary'])
                st.subheader("🔗 Sources Used:",anchor=False)
                for url in result['url_list']:
                    st.write(f'-{url}')
            except Exception as e:
                st.error(f"❌ Error occurred: {e}")

if st.sidebar.button("View Report") and reports:
    topic, urls, report_text = fetch_report_details(selected[0])
    st.subheader(f"📄 Report: {topic}",anchor=False)
    st.write(report_text)

    st.subheader("🔗 Sources",anchor=False)
    for url in urls.split(","):
        st.write(f"- {url}")

