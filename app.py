import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import date
import time
import urllib.parse
import os
import re
import streamlit as st

st.title("⚡ Web Scraping")
st.header(":blue[G]:red[o]:orange[o]:blue[g]:green[l]:red[e] :gray[News]")
st.subheader(" ")
st.subheader(" ")
st.subheader("📍 Bem vindo")
st.text('Esta aplicação permite a realização de Web Scraping de notícias, através do portal Google News.\nPara refinar sua busca, procure utilizar operadores e técnicas de filtragem conhecidas como Google Dorks, para obter melhores resultados.')
st.markdown("[Google Dork commands](https://gist.github.com/sundowndev/283efaddbcf896ab405488330d1bbc06)")
st.divider()


query = st.text_input("Digite as palavras-chave que deseja buscar 🔎", placeholder='Ex: "busca e apreensão", "cartel", "licitação" AND "cartel"...')

buscas_anteriores = ['"busca e apreensão" AND "cartel"',
 '"busca e apreensão" AND "licitação"',
 '"cartel" AND "licitação"',
 '"cartel internacional" -drogas',
 '"conduta anticompetitiva"',
 '"formação de preço"',
 '"cartel de gasolina"',
 '"cartel de combustível"',
 '"cartel em posto de gasolina"',
 '"cartel" AND "merenda" -drogas',
 '"cartel de medicamento"',
 '"fraude em licitação"']

buscas_anteriores = list(set(buscas_anteriores))
consultar_busca = st.checkbox("Histórico 💬")

if consultar_busca:
    st.write("Buscas anteriores: ")
    for i in range(len(buscas_anteriores)):
        st.write(i, " - ", buscas_anteriores[i])
    option = st.text_input("Digite o número correspondente à busca que deseja consultar: ", 0)
    query = buscas_anteriores[int(option)]
    st.write("Opção selecionada: ", query)

st.write(" ")
st.write(" ")
if st.button("⛏⛏⛏SCRAP⛏⛏⛏"):

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

        for i in range(0, len(url_no_dupl)):

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
        time.sleep(1)

        with st.expander("📰 Visualizar notícias"):

            count=0
            for i in data['noticia']:

                with st.chat_message("assistant"):
                        
                    st.write(data['titulo'][count])
                    st.write(i)
                    time.sleep(.5)
                    count += 1


        
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

        download_button = st.download_button(
            label="Download 📤",
            data=csv,
            file_name='noticias.csv',
            mime='text/csv',
        )
