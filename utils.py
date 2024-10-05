import pathlib

from langchain_community.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory

def load_document(temp_filepath):
    ext = pathlib.Path(temp_filepath).suffix
    loaded = PyPDFLoader(temp_filepath)
    docs = loaded.load()
    return docs