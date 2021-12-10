import pandas as pd
import unicodedata
import streamlit as st

st.set_page_config(layout="wide")


file = 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202110_Desonerado.csv'

df = pd.read_csv(file)
df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']].fillna(0).astype(dtype = int)#, errors = 'ignore')

df_insumos = df.loc[df['TIPO ITEM']=='INSUMO',['TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM','UNIDADE ITEM','PRECO UNITARIO']].drop_duplicates()#,'CUSTO TOTAL']]
df_composicao = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO','UNIDADE','CUSTO TOTAL']].drop_duplicates().copy()



st.title('SINAPI Outubro 2021 - Desonerado')

lista_opcoes = ['insumo', 'composicao', 'insumos_composicao']
tipo_busca = st.radio('Tipo de busca', lista_opcoes,0)
palavras = st.text_input('Busca por palavras ou número de composição se "insumos_composicao"')
palavras = unicodedata.normalize('NFKD', palavras).encode('ascii','ignore').decode("utf-8") 


def busca_sinapi(palavras, tipo_busca):
    if tipo_busca=='insumo':
        df_consulta = df_insumos.copy()
        coluna = 'DESCRIÇÃO ITEM'
    elif tipo_busca=='composicao':
        df_consulta = df_composicao.copy()
        coluna = 'DESCRICAO DA COMPOSICAO'
    elif tipo_busca==lista_opcoes[2]:
        df_consulta = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO','TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM','UNIDADE ITEM','PRECO UNITARIO']].copy()
        coluna = 'CODIGO DA COMPOSICAO'
     
    for palavra in palavras.split(' '):
        if tipo_busca!=lista_opcoes[2]:
            df_consulta = df_consulta[df_consulta[coluna].astype(str).str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.contains(palavra.lower())].copy()
        else:
            try :


                st.write(palavra)             
                st.write(df_consulta.loc[df_consulta[coluna]==int(palavras), 'DESCRICAO DA COMPOSICAO'].tolist()[0])
                df_consulta =df_consulta.loc[df_consulta[coluna]==int(palavras), df_consulta.columns[2:]].dropna()

            except:
                print ("Tente um número de composição existente")

    
    return df_consulta

df_busca = busca_sinapi(palavras, tipo_busca)

#set_option('display. max_colwidth', -1)
st.table(df_busca.dropna(thresh=3).reset_index(drop=True))#, 2000, 400)
