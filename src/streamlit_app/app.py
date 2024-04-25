"""Пример работы с чатом через gigachain """

from io import StringIO
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from file_utils import (
    upload_file_or_reject,
    InvalidFileExtension,
    upload_folder,
    output_folder,
)

from chain_utils import (
    get_llm,
    get_embedder,
    process_all_uploaded_files,
    GLOBAL_PROMPTS,
)

st.title("Gracula 🧛‍♂️🧛‍♀️")


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


def run_extraction(json_cfg):
    print("EXTRACTION IN PROGRESS...")
    progress_text = "Operation in progress. Please wait. Attention: The process could take long (avg 15 sec/paper)"
    my_bar = st.progress(0, text=progress_text)

    df = process_all_uploaded_files(
        llm=llm,
        embeddings=embeddings,
        prompts=GLOBAL_PROMPTS,
        cfg=json_cfg,
        bar=my_bar,
    )
    print("EXTRACTION FINISHED.")
    # print(type(state))
    df = pd.DataFrame(df)
    df.to_csv(output_folder / "result.csv")


with st.sidebar:
    st.title("GIGACHAT API")
    base_url = st.selectbox(
        "GIGACHAT_BASE_URL",
        (
            "https://gigachat.devices.sberbank.ru/api/v1",
            "https://beta.saluteai.sberdevices.ru/v1",
        ),
    )
    st.title("Авторизационные данные")
    credentials = st.text_input("GIGACHAT_CREDENTIALS", type="password")
    scope = st.selectbox(
        "GIGACHAT_SCOPE",
        (
            "GIGACHAT_API_CORP",
            "GIGACHAT_API_PERS",
        ),
    )
    st.title("OR")
    access_token = st.text_input("GIGACHAT_ACCESS_TOKEN", type="password")
    st.title("OR")
    user = st.text_input("GIGACHAT_USER")
    password = st.text_input("GIGACHAT_PASSWORD", type="password")

llm = get_llm(
    base_url=base_url,
    credentials=credentials,
    access_token=st.session_state.get("token") or access_token,  # Переиспользуем токен
    user=user,
    password=password,
    scope=scope,
)
embeddings = get_embedder(
    base_url=base_url,
    credentials=credentials,
    access_token=st.session_state.get("token") or access_token,  # Переиспользуем токен
    user=user,
    password=password,
    scope=scope,
)

# Upload paper pdf files
uploaded_files = st.file_uploader(
    "Choose paper files to upload", accept_multiple_files=True
)

for uploaded_file in uploaded_files:
    try:
        upload_file_or_reject(uploaded_file, upload_folder)
    except InvalidFileExtension as e:
        st.write(e)


## upload config (TEMP measure)
uploaded_config = st.file_uploader("Choose a config file")
if uploaded_config is not None:
    # To convert to a string based IO:
    stringio = StringIO(uploaded_config.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()
    st.code(string_data)
    json_cfg = json.loads(string_data)

    st.button(label="Run extraction", on_click=run_extraction, args=[json_cfg])

    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    result_df = pd.read_csv(output_folder / "result.csv")

    csv = convert_df(result_df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="result.csv",
        mime="text/csv",
    )
