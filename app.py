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

db = database.conect_db()
database.create_tables()
NER = spacy.load('pt_core_news_lg')

with st.container():
    st.image("cade-logo.jpg", width=300)


tab1, tab2 = st.tabs(["📰 Crawler", "📞 Ajuda"])

with tab1:

    st.title("🚨 Observatório da Concorrência")
    st.header("")
    st.subheader(" ")
    st.subheader("📍 :gray[Bem vindo]")
    st.text('Esta aplicação permite a realização de Web Scraping de notícias, através do portal Google News.\nPara refinar sua busca, procure utilizar operadores e técnicas de filtragem conhecidas como Google Dorks, para obter melhores resultados.')
    st.markdown("[Google Dork commands](https://gist.github.com/sundowndev/283efaddbcf896ab405488330d1bbc06)")
    st.divider()


    query = st.text_input("Digite as palavras-chave que deseja buscar 🔎", placeholder='Ex: "busca e apreensão", "cartel", "licitação" AND "cartel"...')

    historico_dias = list(set(database.get_dia()))


    consultar_busca = st.checkbox("Histórico 💬")

    if consultar_busca:

        dia_selecionado = st.selectbox("Selecione o dia que deseja consultar: ", historico_dias)
        buscas_anteriores = list(set(database.get_busca(dia_selecionado)))
        query = st.radio("Selecione a busca que deseja consultar: ", buscas_anteriores)


    st.write(" ")
    st.write(" ")
    if st.button("⛏⛏⛏SCRAP⛏⛏⛏"):
        database.insert_query(query, dia=date.today())
        with st.spinner('Aguarde enquanto os dados são carregados...'):
        
            entrada_user = query
            print("\n\nOpção selecionada:\n")
            print(entrada_user)


            query = entrada_user
            query_encode = query.replace(' ', '+')

            url_base = 'https://news.google.com/search?q={}&hl=pt-BR&gl=BR&ceid=BR:pt-419'.format(query_encode)


            response = requests.get(url_base)

            if response.status_code == 200:
                print('Requisição bem sucedida!')
                content = response.content
            else:
                print('Erro na requisição!')



            soup = BeautifulSoup(content, "html.parser")

            divs = soup.find_all("div", class_="xrnccd")

            hrefs = []
            for div in divs:
                a_tags = div.find_all("a")
                for a in a_tags:
                    href = a.get("href")
                    if href is not None:
                        hrefs.append(href)

            # print the list of hrefs
            print(len(hrefs))


            hrefs = [k for k in hrefs if 'articles/' in k]
            url_noticias = []
            for i in hrefs:
                url_noticias.append(i.replace('./', 'https://news.google.com/'))

            tamanho_original = len(url_noticias)
            url_no_dupl = list(set(url_noticias))
            tamanho_sem_duplicados = len(url_no_dupl)

            st.success("Foram encontrados {} links.".format(tamanho_original))
            time.sleep(.5)
            st.warning("Verificando itens duplicados ..")
            time.sleep(2)
            st.warning("Removendo itens duplicados ..")
            time.sleep(1)
            st.success("Remoção concluída, sobraram {} itens.".format(tamanho_sem_duplicados))



            def remove_tags(html):
            
                # parse html content
                soup = BeautifulSoup(html, "html.parser")
            
                for data in soup(['style', 'script']):
                    # Remove tags
                    data.decompose()
            
                # return data by retrieving the tag content
                return '\n'.join(soup.stripped_strings)



            fonte = []
            conteudo = []
# FILTRANDO APENAS AS 5 PRIMEIRAS (para verificar todas, trocar o 5 por len(url_no_dupl)))
            for i in range(0, 5):

                try:
                    response = requests.get(url_no_dupl[i])

                    if response.status_code == 200:
                        print('Requisição bem sucedida!')
                        print("")
                        html = response.content
                        fonte.append(url_no_dupl[i])
                        conteudo.append(remove_tags(html))
                        st.toast("🔥 Notícia identificada: \n" + str(remove_tags(html).split('\n')[0]))
                    else:
                        print('Erro na requisição!')
                        print("")
                
                except Exception as e:
                    print(e)
                    print("")




            zip_list = list(zip(fonte, conteudo))
            data_content = pd.DataFrame(zip_list, columns = ['fonte', 'conteudo'])



            titulo = []

            for i in data_content['conteudo']:
                first_line = i.split('\n')[0]
                titulo.append(first_line)


            data_content['titulo'] = titulo
            data = data_content.copy()


            matrix = []
            content = []
            df_test = pd.DataFrame()
            for i in data['conteudo']:
                content.append(i.split('\n'))

            matrix.append(content)


            clean_data = []
            for i in matrix[0]:
                print("Tamanho original: " + str(len(i)))
                i = list(filter(lambda x: len(x) > 50, i))
                print("Tamanho final: " + str(len(i)))
                print("")

                print(list(i))
                clean_data.append(i)


            news_to_df = []
            for new in clean_data:
                news_to_df.append(' '.join(new))



            data['noticia'] = news_to_df
            data.drop(columns=['conteudo'], inplace=True)

            st.success("Foram encontradas {} notícias.".format(len(data['noticia'])))
            st.write(" ")
            time.sleep(.5)

            for i, j, k in zip(data['titulo'], data['noticia'], data['fonte']):
                database.inserir_noticias(i, j, k)

           
        with st.status("Preparando arquivo para Download 💾", expanded=True) as status:
            time.sleep(2)
            st.write("✂ Selecionando os dados ...")
            st.write("⚙ Escrevendo os dados em um arquivo .csv...")
            time.sleep(3)
            st.write("✅ Pronto! Arquivo criado com sucesso!")
            st.toast("Você já pode baixar o arquivo 🎉")
            time.sleep(1)


            @st.cache_data
            def convert_df(df):
                return df.to_csv().encode('utf-8')

            csv = convert_df(data)
            today = str(date.today())


            download_button = st.download_button(
                label="Download 📤",
                data=csv,
                file_name='{}_{}.csv'.format(today, query_encode).replace('+', '-'),
                mime='text/csv',
            )