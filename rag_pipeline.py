import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from data_loader import load_excel_as_documents
from settings import MODEL_EMBEDDINGS, MODEL_LLM, OLLAMA_HOST


CHROMA_DIR = "chroma_db"


def build_vectorstore():
    print("STEP 1: Loading documents...")
    docs = load_excel_as_documents()

    print(f"STEP 2: Loaded {len(docs)} docs, creating embeddings...")
    embeddings = OllamaEmbeddings(model=MODEL_EMBEDDINGS, base_url=OLLAMA_HOST)

    print("STEP 3: Building Chroma index...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )

    print("STEP 4: Chroma index saved.")
    return vectorstore


def load_vectorstore():
    print("Loading existing Chroma index...")
    embeddings = OllamaEmbeddings(model=MODEL_EMBEDDINGS, base_url=OLLAMA_HOST)

    return Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )


def build_qa():


    if os.path.exists(CHROMA_DIR):

        vs = load_vectorstore()
    else:

        vs = build_vectorstore()


    retriever = vs.as_retriever(search_kwargs={"k": 10})


    llm = ChatOllama(
        model=MODEL_LLM,
        base_url=OLLAMA_HOST,
        temperature=0.2
    )


    prompt = ChatPromptTemplate.from_template("""
Usa SOLO este contexto para responder y nunca inventes información.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
""")

    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    print("==== build_qa complete ====")
    return rag_chain
