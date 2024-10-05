import os
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import BaseRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import DocArrayInMemorySearch
from utils import load_document
from groq_api_key import my_groq_key

LLM = ChatGroq(model="llama3-70b-8192", groq_api_key=my_groq_key)

def configure_retriever(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"Number of chunks: {len(splits)}")  # Debug output

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)
    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 7,
            "include_metadata": True
        },
    )
    return retriever


def configure_chain(retriever):
    params = dict(
        llm=LLM,
        retriever=retriever,
        verbose=True,
        max_tokens_limit=4000,
    )
    return ConversationalRetrievalChain.from_llm(**params)


def load_permanent_document():
    permanent_doc_path = "./books_summary_merged.pdf"
    if not os.path.exists(permanent_doc_path):
        raise FileNotFoundError(f"Document not found at path: {permanent_doc_path}")
    return load_document(permanent_doc_path)

def configure_retrieval_chain():
    docs = load_permanent_document()

    retriever = configure_retriever(docs=docs)
    chain = configure_chain(retriever=retriever)
    return chain