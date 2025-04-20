import asyncio
import logging
from langchain_community.vectorstores import FAISS
from embadings import embadings_model
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.memory import ConversationBufferMemory
from langchain.chains import conversational_retrieval
import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)

LANGSMITH_TRACING=True
LANGSMITH_ENDPOINT=os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY=os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT=os.getenv("LANGSMITH_PROJECT")

def llm():
    try:
        return init_chat_model("gpt-4o-mini", model_provider="openai")
    except:
        return "chat model not invoked"
def  vectorstore_load():
    try:
        return FAISS.load_local("cbc-index", embeddings=embadings_model(),allow_dangerous_deserialization=True)
    except Exception as e:
        logging.info("DB not loaded")
        return "Vector db not loaded"
memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question",
            return_messages=True
        )
async def generate_response(query):
    try:
        vectorstore = vectorstore_load()
        retrieved_docs = vectorstore.similarity_search(query, k=5)
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt_runnable = hub.pull("rlm/rag-prompt")  # pulled correctly
        chain = prompt_runnable | llm() | StrOutputParser()
        memory.chat_memory.add_user_message(query)
        response = await chain.ainvoke({"question": query, "context": context})
        memory.chat_memory.add_ai_message(response)
        return response
    except Exception as e:
        logging.info("error for getting reponse from AI")
        return " error for getting reponse from AI"


#if __name__ == "__main__":
    #asyncio.run(generate_response(query))






