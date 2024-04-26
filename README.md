# 📙 Description

Gracula🧛‍♂️🧛‍♀️ is an AI-agent-based scientific papers extractor. It uses GigaChat API to analyse user-uploaded PDF files and build a compilation table dataset out of them. [Accessible on Sreamlit.](https://gracula.streamlit.app/)

# ⚙️ How to install
If one needs to deploy a local solution, there are the stages below.

After cloning the repository, run the code below in a root directory `gracula` to install essential packages.

```pip install requirements.txt```

# ☀️ How to use

## 🌱 how to open interface
Once requirements have been installed, the website should open locally with Streamlit on the port specified.

```streamlit run "/src/streamlit_app/app.py" --server.port ####```

Once deployed, one needs to share the GigaChat credentials in the field `GIGACHAT_CREDENTIALS` in order to use [GigaChat API](https://developers.sber.ru/docs/ru/gigachat/api/overview).

# 🔗 Share
If you find this project useful, consider citing this repository. We are longing for your feedback! 🧛‍♂️🧛‍♀️