from  generator import  generate_response,memory
import asyncio

import streamlit as st
st.title("CBC Chat Bot for internal use")
query = st.text_area("Enter your question:", height=200)

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]

if st.button("Submit"):
    if query.strip() == "":
        st.warning("Please enter a question before submitting.")
    else:
        with st.spinner("Generating response..."):
            response = asyncio.run(generate_response(query))
            st.session_state.chat_history.append(("User",query))
            st.session_state.chat_history.append(("AI",response))


            st.success("Response:")
            st.write(response)
        for role, msg in reversed(st.session_state.chat_history):
            if role == "User":
                st.markdown(f"USER  : {msg}")
            else:
                st.markdown(f"BOT : {msg}")


