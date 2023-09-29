import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
from spacy import displacy
import spacy_streamlit
from spacy_streamlit import visualize_ner
from pathlib import Path
from datetime import date
import time
import urllib.parse
import os
import re
import streamlit as st
import sqlite3
import services.database as database
st. set_page_config(layout="wide")

NER = spacy.load('pt_core_news_lg')




st.title("📊 Análise de dados")


with st.spinner("🔎 Identificando entidades.."):
    time.sleep(1.5)
    st.success("Concluído!")


st.subheader("📰 Notícia selecionada:")    
titulo_select = st.selectbox("Escolha:", database.select_titulo())
index_titulo = database.select_titulo().index(titulo_select)
noticias = database.select_noticias()
noticia = noticias[index_titulo]

doc = NER(noticia)
visualize_ner(doc, labels=NER.get_pipe('ner').labels)




#for i in noticias:
#    doc = NER(i)
#    visualize_ner(doc, labels=NER.get_pipe('ner').labels)