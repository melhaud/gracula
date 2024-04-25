from typing import Any

import glob
import pandas as pd
import json
from PyPDF2 import PdfReader

from pathlib import Path


from langchain.chat_models.gigachat import GigaChat

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import GigaChatEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import CommaSeparatedListOutputParser

from file_utils import SCRIPT_PATH, upload_folder

CONTEXT_BASED_Q_TEMPLATE = """Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}
"""

GLOBAL_PROMPTS = json.load(open(SCRIPT_PATH / "prompts.json", "r"))

csv_parser = CommaSeparatedListOutputParser()

format_instructions = csv_parser.get_format_instructions()

prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": csv_parser.get_format_instructions()},
)
json_parser = JsonOutputParser()


def get_llm(**kwargs) -> Any:
    """Construct single LLM object for all uses."""
    cfg = json.load(open(SCRIPT_PATH / "llm_cfg.json", "r"))
    cfg.update(**kwargs)
    llm = GigaChat(**cfg)
    return llm


def get_embedder(**kwargs) -> Any:
    """Construct single embedder object for all uses."""
    cfg = {"verify_ssl_certs": False}
    cfg.update(**kwargs)
    embeddings = GigaChatEmbeddings(**cfg)
    return embeddings


def extract_raw_text_from_pdf(path) -> str:
    """Extract raw text from pdf."""
    reader = PdfReader(stream=path)

    raw_text = ""
    for _, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text

    return raw_text


def get_index_from_raw_text(text, embeddings) -> Any:
    """Construct vector store from pdf"""
    text_splitter = RecursiveCharacterTextSplitter(
        # separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(text=text)

    index = FAISS.from_texts(texts=texts, embedding=embeddings)
    return index


def get_doc_chain(llm, template, prompt):
    """Construct single DocumentStuffChain"""
    prompt = ChatPromptTemplate.from_template(template)
    return create_stuff_documents_chain(llm, prompt)


def get_retrieval_chain(index, doc_chain):
    """Construct sinle RetrievalChain"""
    retriever = index.as_retriever()
    return create_retrieval_chain(retriever, doc_chain)


def get_paper_processing_chain(path, llm, embeddings, prompts, cfg) -> pd.DataFrame:

    ## 1. get paper name and raw text from pdf
    paper_name = Path(path).stem
    raw_text = extract_raw_text_from_pdf(path=path)

    ## 2. create index from raw text
    index = get_index_from_raw_text(raw_text, embeddings=embeddings)

    ## 3. create doc chain
    doc_chain = get_doc_chain(
        llm=llm,
        template=CONTEXT_BASED_Q_TEMPLATE,
        prompt=prompts["LIST_OBJECTS_PROMPT"].format(**cfg),
    )

    ## 4. get retrieval chain
    retrieve_chain = get_retrieval_chain(index=index, doc_chain=doc_chain)

    ## 5. construct obj list retrieval chain
    obj_list_retrieval_chain = (
        retrieve_chain
        | RunnableLambda(func=lambda x: x["answer"].strip("[]"))
        | csv_parser
    )

    ## 6. construct obj properties retrieval chain
    obj_props_retrieval_chain = (
        retrieve_chain
        | RunnableLambda(
            func=lambda x: x["answer"]
            .replace("'", '"')
            .replace("None", "null")
            .replace("False", "false")
            .replace("True", "true")
        )
        | json_parser
    )

    ## 7. retrieve list of objects
    chat_history = [
        SystemMessage(content=prompts["SYSTEM_PROMPT"]),
        AIMessage(content="Ok! Let's get to work!"),
    ]

    objs = obj_list_retrieval_chain.invoke(
        {
            "chat_history": chat_history,
            "input": prompts["LIST_OBJECTS_PROMPT"].format(**cfg),
        }
    )

    ## 8. retrieve properties of objects
    objs_props = []
    for obj in objs:
        props = obj_props_retrieval_chain.invoke(
            {
                "chat_history": chat_history,
                "input": prompts["LIST_PROPERTIES_PROMPT"].format(obj=obj, **cfg),
            }
        )
        props["paper"] = paper_name
        objs_props.append(props)

    return objs_props


def process_all_uploaded_files(llm, embeddings, prompts, cfg, bar=None) -> pd.DataFrame:
    all_objs = []
    paths = glob.glob(
        str(upload_folder) + "/*.pdf",
    )
    print(paths)
    if len(paths) == 0:
        return []
    progress_bar_step = 0.99 / len(paths)
    for i, path in enumerate(paths):
        response = get_paper_processing_chain(
            path=path,
            llm=llm,
            embeddings=embeddings,
            prompts=prompts,
            cfg=cfg,
        )
        all_objs.extend(response)
        if bar:
            bar.progress((i + 1) * progress_bar_step)  # upd progress bar

    return all_objs
