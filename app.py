import streamlit as st
import asyncio
from orchestrator import build_graph

st.set_page_config(page_title="Nova Tech Graph AI", page_icon="🕸️", layout="centered")

st.title("🕸️ Nova Tech Knowledge Graph Agent")
st.markdown("A 2026-Ready Agentic AI querying an enterprise Neo4j Knowledge Graph.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about Nova Tech Solutions..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent generating Cypher & Reasoning..."):
            graph = build_graph()
            
            try:
                result = asyncio.run(graph.ainvoke({
                    "question": prompt,
                    "entities": [],
                    "graph_facts": [],
                    "answer": ""
                }))
                answer = result['answer']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error execution graph logic: {e}")
