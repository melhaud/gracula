"""Пример работы с чатом через gigachain """

from io import StringIO
from pathlib import Path
import streamlit as st

# Try demo - https://gigachat-streaming.streamlit.app/

from langchain_community.chat_models import GigaChat
from file_utils.file_utils import (
    upload_file_or_reject,
    prepare_results_dataframe,
    InvalidFileExtension,
    OUTPUT_FOLDER,
    UPLOAD_FOLDER,
)

upload_folder = Path(__file__).resolve().parent / UPLOAD_FOLDER
output_folder = Path(__file__).resolve().parent / OUTPUT_FOLDER
# from langchain.schema import ChatMessage

st.title("Gracula 🧛‍♂️🧛‍♀️")

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
    scope = st.text_input("GIGACHAT_SCOPE", type="password")
    st.title("OR")
    access_token = st.text_input("GIGACHAT_ACCESS_TOKEN", type="password")
    st.title("OR")
    user = st.text_input("GIGACHAT_USER")
    password = st.text_input("GIGACHAT_PASSWORD", type="password")

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
st.session_state["uploaded_config"] = uploaded_config
if uploaded_config is not None:
    # To convert to a string based IO:
    stringio = StringIO(uploaded_config.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()
    st.code(string_data)


# Here should all the `gigachain` staff lie
# chat = GigaChat(
#     base_url=base_url,
#     credentials=credentials,
#     scope=scope,
#     access_token=st.session_state.get("token") or access_token,  # Переиспользуем токен
#     user=user,
#     password=password,
#     verify_ssl_certs=False,
# )


@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")


result_df = prepare_results_dataframe(output_folder)

csv = convert_df(result_df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name="result.csv",
    mime="text/csv",
)
