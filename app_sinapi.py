import pandas as pd
import unicodedata
import streamlit as st

st.set_page_config(layout="wide")

file = 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202111_Desonerado.csv'
file_insumos_ficha = 'Arquivos A a Z.csv'
file_insumos_ficha_marcas = 'Arquivos A a Z_com_marcas.csv'

df = pd.read_csv(file)
df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM',
                                                  'CODIGO DA COMPOSICAO']].fillna(0) \
    .astype(dtype=int)  # , errors = 'ignore')

df_ficha = pd.read_csv(file_insumos_ficha)
df_ficha_marcas = pd.read_csv(file_insumos_ficha_marcas)

df_insumos = df.loc[df['TIPO ITEM'] == 'INSUMO',
                    ['TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM',
                     'UNIDADE ITEM', 'PRECO UNITARIO']] \
    .drop_duplicates()  # ,'CUSTO TOTAL']]

df_composicao = df[['CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
                    'UNIDADE', 'CUSTO TOTAL']].drop_duplicates().copy()

lista_opcoes = ['insumo', 'composicao', 'insumos_composicao', 'ficha_especificacao', 'ficha_especificacao_com_marcas']


def tabela_tipo_sinapi(tipo_busca):
    if tipo_busca == 'insumo':
        df_consulta = df_insumos.copy()
        coluna = 'DESCRIÇÃO ITEM'
    elif tipo_busca == 'composicao':
        df_consulta = df_composicao.copy()
        coluna = 'DESCRICAO DA COMPOSICAO'
    elif tipo_busca == lista_opcoes[2]:
        df_consulta = df[['CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
                          'TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM',
                          'UNIDADE ITEM', 'PRECO UNITARIO']].copy()

        coluna = 'CODIGO DA COMPOSICAO'
    elif tipo_busca == lista_opcoes[3]:
        df_consulta = df_ficha[df_ficha.columns[1:]]
        coluna = 'Descrição Básica'
    elif tipo_busca == lista_opcoes[4]:
        df_consulta = df_ficha_marcas[df_ficha_marcas.columns[1:]]
        coluna = 'Referencial / Parâmetro de Pesquisa'

    return df_consulta, coluna

def busca_sinapi(palavras, tipo_busca, coluna, df_consulta, lista_palavras):
    if all(flag == '' for (flag) in lista_palavras):
        for palavra in palavras.split(' '):
            #
            df_consulta = df_consulta[df_consulta[coluna].astype(str) \
                .astype(str).str.lower() \
                .str.normalize('NFKD') \
                .str.encode('ascii', errors='ignore') \
                .str.decode('utf-8') \
                .str.contains(palavra.lower())].copy()
            # else:
            #
            #     st.write(palavra)


    else:
        for palavras_cj, coluna in zip(lista_palavras, df_consulta.columns):
            for palavra in palavras_cj.split(' '):

                df_consulta = df_consulta[df_consulta[coluna]\
                    .astype(str)\
                    .astype(str).str.lower() \
                    .str.normalize('NFKD') \
                    .str.encode('ascii', errors='ignore') \
                    .str.decode('utf-8') \
                    .str.contains(palavra.lower())].copy()

    if tipo_busca == lista_opcoes[2]:
        st.write(df_consulta.loc[:, 'DESCRICAO DA COMPOSICAO'].tolist()[0])
        df_consulta = df_consulta.loc[:, df_consulta.columns[2:]].dropna()

    return df_consulta

st.title('SINAPI Novembro 2021 - Desonerado')

tipo_busca = st.radio('Tipo de busca', lista_opcoes, 0)

df_busca_, coluna = tabela_tipo_sinapi(tipo_busca)

palavras = st.text_input('Busca por palavras ou número de composição se "insumos_composicao"')
palavras = unicodedata.normalize('NFKD', palavras).encode('ascii', 'ignore').decode("utf-8")

lista_palavras = []
with st.expander("Busca Avançada"):
    # st.text(df_busca_.columns)
    # tipo_busca_avancada = st.checkbox('Busca Avançada')
    nomes_colunas = df_busca_.columns
    n_colunas = len(nomes_colunas)
    cols = st.columns(n_colunas)
    for nome, col in zip(nomes_colunas, cols):
        lista_palavras.append(col.text_input(nome))

# st.text(lista_palavras)

df_busca = busca_sinapi(palavras, tipo_busca, coluna, df_busca_, lista_palavras)

# set_option('display. max_colwidth', -1)
st.table(df_busca.dropna(thresh=3).reset_index(drop=True))  # , 2000, 400)





# #http://www.sinapi.ibge.gov.br/Catalogo_Insumos/Imprimir_Catalogo/?cod_ibge=7005

# import pandas as pd
# import unicodedata
# import streamlit as st

# st.set_page_config(layout="wide")


# file = 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202111_Desonerado.csv'
# file_insumos_ficha = 'Arquivos A a Z.csv'
# file_insumos_ficha_marcas = 'Arquivos A a Z_com_marcas.csv'

# df = pd.read_csv(file)
# df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM',
#                                                   'CODIGO DA COMPOSICAO']].fillna(0)\
#                                                     .astype(dtype = int)#, errors = 'ignore')

# df_ficha = pd.read_csv(file_insumos_ficha)
# df_ficha_marcas = pd.read_csv(file_insumos_ficha_marcas)

# df_insumos = df.loc[df['TIPO ITEM']=='INSUMO',
#                     ['TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM',
#                      'UNIDADE ITEM','PRECO UNITARIO']]\
#                         .drop_duplicates()#,'CUSTO TOTAL']]

# df_composicao = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO',
#                     'UNIDADE','CUSTO TOTAL']].drop_duplicates().copy()



# st.title('SINAPI Novembro 2021 - Desonerado')

# lista_opcoes = ['insumo', 'composicao', 'insumos_composicao', 'ficha_especificacao', 'ficha_especificacao_com_marcas']
# tipo_busca = st.radio('Tipo de busca', lista_opcoes,0)
# palavras = st.text_input('Busca por palavras ou número de composição se "insumos_composicao"')
# palavras = unicodedata.normalize('NFKD', palavras).encode('ascii','ignore').decode("utf-8") 


# def busca_sinapi(palavras, tipo_busca):
#     if tipo_busca=='insumo':
#         df_consulta = df_insumos.copy()
#         coluna = 'DESCRIÇÃO ITEM'
#     elif tipo_busca=='composicao':
#         df_consulta = df_composicao.copy()
#         coluna = 'DESCRICAO DA COMPOSICAO'
#     elif tipo_busca==lista_opcoes[2]:
#         df_consulta = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO',
#                           'TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM',
#                           'UNIDADE ITEM','PRECO UNITARIO']].copy()

#         coluna = 'CODIGO DA COMPOSICAO'
#     elif tipo_busca==lista_opcoes[3]:
#         df_consulta = df_ficha[df_ficha.columns[1:]]
#         coluna='Descrição Básica'
#     elif tipo_busca==lista_opcoes[4]:
#         df_consulta = df_ficha_marcas[df_ficha_marcas.columns[1:]]
#         coluna='Referencial / Parâmetro de Pesquisa'
     
#     for palavra in palavras.split(' '):
#         if tipo_busca!=lista_opcoes[2]:
#             df_consulta = df_consulta[df_consulta[coluna]\
#                 .astype(str).str.lower()\
#                 .str.normalize('NFKD')\
#                 .str.encode('ascii', errors='ignore')\
#                 .str.decode('utf-8')\
#                 .str.contains(palavra.lower())].copy()
#         else:
            

#             st.write(palavra)             
#             st.write(df_consulta.loc[df_consulta[coluna]==int(palavras), 'DESCRICAO DA COMPOSICAO'].tolist()[0])
#             df_consulta =df_consulta.loc[df_consulta[coluna]==int(palavras), df_consulta.columns[2:]].dropna()
    
    
#     return df_consulta

# df_busca = busca_sinapi(palavras, tipo_busca)

# #set_option('display. max_colwidth', -1)
# st.table(df_busca.dropna(thresh=3).reset_index(drop=True))#, 2000, 400)
