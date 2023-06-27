import os

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings


def run_query(query, dataset_source_path, dataset_store_path):
    _add_docs_deeplake_db(dataset_source_path, dataset_store_path)
    retriever = _retrieve_deeplake_data(dataset_store_path)
    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=retriever,
    )
    return chain.run(query)


def _get_docs(dir):
    docs = []
    for dirpath, dirnames, filenames in os.walk(dir):
        for file in filenames:
            try:
                loader = TextLoader(os.path.join(dirpath, file), encoding="utf-8")
                docs.extend(loader.load_and_split())
            except Exception as e:
                pass
    return docs


def _get_splittered_text(docs):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    return text_splitter.split_documents(docs)


def _get_embiddings():
    return OpenAIEmbeddings(disallowed_special=())


def _add_docs_deeplake_db(dataset_source_path, dataset_store_path):
    docs = _get_docs(dataset_source_path)
    texts = _get_splittered_text(docs)
    db = DeepLake(dataset_path=dataset_store_path, embedding_function=_get_embiddings())
    db.add_documents(texts)


def _retrieve_deeplake_data(dataset_store_path):
    db = DeepLake(dataset_path=dataset_store_path, embedding_function=_get_embiddings())
    return db.as_retriever(
        search_kwargs={
            "k": 1,
            "distance_metric": "cos",
            "fetch_k": 100,
            "maximal_marginal_relevance": True,
        }
    )
