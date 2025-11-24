import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from data_loader import load_excel_as_documents
from settings import MODEL_EMBEDDINGS, MODEL_LLM, OLLAMA_HOST

CHROMA_DIR = "chroma_db"

def detect_intent(question: str) -> str:
    q = question.lower()
    if any(w in q for w in ["producto", "productos", "vendieron", "ventas por producto"]):
        return "producto"
    if any(w in q for w in ["cliente", "clientes", "compró", "compraron"]):
        return "cliente"
    if any(w in q for w in ["categoría", "categoria", "categorias"]):
        return "categoria"
    if any(w in q for w in ["mes", "marzo", "abril", "enero", "febrero", "2023", "2022"]):
        return "mes"
    return "general"

def build_vectorstore():
    docs = load_excel_as_documents()
    embeddings = OllamaEmbeddings(model=MODEL_EMBEDDINGS, base_url=OLLAMA_HOST)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    return vectorstore

def load_vectorstore():
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

    def get_retriever_for_intent_local(question):
        intent = detect_intent(question)
        if intent == "producto":
            filters = {"$or": [
                {"tipo": "producto_agg"},
                {"tipo": "producto_totales_global"},
                {"tipo": "faq_productos"},
                {"tipo": "global"}
            ]}
            return vs.as_retriever(search_kwargs={"k": 15, "filter": filters})
        if intent == "cliente":
            filters = {"tipo": "cliente_totales_global"}
            return vs.as_retriever(search_kwargs={"k": 12, "filter": filters})
        if intent == "categoria":
            filters = {"tipo": "categoria_agg"}
            return vs.as_retriever(search_kwargs={"k": 10, "filter": filters})
        if intent == "mes":
            filters = {"tipo": "mes_agg"}
            return vs.as_retriever(search_kwargs={"k": 10, "filter": filters})
        return vs.as_retriever(search_kwargs={"k": 10})

    def retrieve_docs(input_value):
        q = input_value if isinstance(input_value, str) else input_value["question"]
        retriever = get_retriever_for_intent_local(q)
        return retriever.invoke(q)

    llm = ChatOllama(
        model=MODEL_LLM,
        base_url=OLLAMA_HOST,
        temperature=0.1
    )

    prompt = ChatPromptTemplate.from_template("""
Usa SOLO este contexto para responder y nunca inventes información.
Si el contexto contiene información agregada, respóndela directamente.
No listes cada producto si existe un resumen total.
No inventes cálculos adicionales.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
""")

    rag_chain = (
        {
            "context": retrieve_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )

    return rag_chain
