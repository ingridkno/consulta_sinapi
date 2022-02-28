import pandas as pd
import unicodedata
import streamlit as st
import os
import numpy as np

st.set_page_config(layout="wide")

encargo_mensalista_sem_desoneracao = 70.94
encargo_horista_sem_desoneracao = 112.75

BDI_contratao = 22.12

col1, col2= st.columns([2, 7])
with col1.expander('Parâmetros'):
    base_sinapi = st.selectbox('Base SINAPI', ('Dezembro 2021', 'Janeiro 2022'))
    BDI = st.text_input('Taxa BDI aplicada', str(BDI_contratao))
    BDI = float(BDI)

ano_base_sinapi = base_sinapi.split(' ')[1]
mes_base_sinapi = base_sinapi.split(' ')[0]

mes_numero = {'Janeiro':'01', 'Dezembro':'12'}

#cod_base_sinapi_data =
ref_mes = ("_".join(base_sinapi.split()))
path_data = os.path.join('./data')

if base_sinapi=='Janeiro 2022':
    file = os.path.join(path_data, ref_mes, 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202201_NaoDesonerado.xls')
    file_insumos_custo= os.path.join(path_data, ref_mes, 'SINAPI_Preco_Ref_Insumos_SC_012022_NaoDesonerado.xls')
elif base_sinapi=='Dezembro 2021':
    file = os.path.join(path_data, ref_mes, 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202112_NaoDesonerado.xls')
    file_insumos_custo= os.path.join(path_data, ref_mes, 'SINAPI_Preco_Ref_Insumos_SC_202112_NaoDesonerado.xls')

file_insumos_ficha = os.path.join(path_data, ref_mes, 'Arquivos A a Z_'+ref_mes+'.csv')

file_insumos_ficha_marcas = 'Arquivos A a Z_com_marcas.csv'
file_codigos_caixa_ibge = 'codigo_ibge_caixa.csv'
imagem_path = 'Imagens'

#df_X = pd.read_excel(file, header=5)
#df_X.to_csv(file[:-3]+'csv')

st.write(file)
df = pd.read_csv(file[:-3]+'csv')

df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM',
                                                  'CODIGO DA COMPOSICAO']].fillna(0) \
    .astype(dtype=int)  # , errors = 'ignore')

df_ficha = pd.read_csv(file_insumos_ficha)
df_ficha_marcas = pd.read_csv(file_insumos_ficha_marcas)
cod_ibge_caixa = pd.read_csv(file_codigos_caixa_ibge)
cod_ibge_caixa = cod_ibge_caixa[['cod_ibge','cod_caixa']].fillna(0).astype(int)#.astype(str)
link ='http://www.sinapi.ibge.gov.br/Catalogo_Insumos/Imprimir_Catalogo/?cod_ibge='


#df_insumos = pd.read_excel(file_insumos_custo, header=6)
#df_insumos.to_csv(file_insumos_custo[:-3] +'csv')
df_insumos= pd.read_csv(file_insumos_custo[:-3]+'csv')
df_insumos = df_insumos[df_insumos.columns[1:]]


df_composicao = df[['CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
                    'UNIDADE', 'CUSTO TOTAL']].drop_duplicates().copy()

df_ficha = df_ficha.merge(cod_ibge_caixa, left_on='Código do SINAPI', right_on='cod_caixa', how='left').drop(columns=['cod_caixa'])
df_ficha_marcas = df_ficha_marcas.merge(cod_ibge_caixa, left_on='Código do SINAPI', right_on='cod_caixa', how='left').drop(columns=['cod_caixa'])
#df_insumos = df_insumos.merge(cod_ibge_caixa, left_on="CODIGO  ", right_on='cod_caixa', how='left').drop(columns=['cod_caixa'])
#st.write(df_insumos.columns.tolist())
# file_imagens = os.path.join(imagem_path, 'A_A_df_imagens_referencia.csv')
# df_imagem = pd.read_csv(file_imagens)
# df_imagem['arquivo'] = 'janeiro_2022 - FichaInsumo\\'+df_imagem['arquivo']+'.pdf' #
# df_imagem = df_imagem.rename(columns={'arquivo':'Arquivo'})
#df_ficha = df_ficha.merge(df_imagem, on=['pagina', 'Arquivo'], how='outer')

#descartar colunas
df_ficha.drop(['Normas Técnicas', 'Imagem', 'Obs', 'pagina', 'Arquivo', 'Atualizado em'], axis=1, inplace=True)
#juntar dataframes para colocar marcas na ficha de insumo mais recente
df_ficha = df_ficha.merge(df_ficha_marcas[['Código do SINAPI', 'Referencial / Parâmetro de Pesquisa']], how='left', on='Código do SINAPI')

def transformacao_string_numero(coluna, df, n=2):
    df[coluna] = pd.to_numeric(df[coluna].str.replace('.', '').str.replace(',', '.'), errors='ignore')
    df[coluna+' com BDI'] = round(df[coluna]*(1+(BDI/100)), n)
    return df

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = link.split('=')[1]
    return f'<a target="_blank" href="{link}">{text}</a>'


df_ficha['cod_ibge'] = link+df_ficha['cod_ibge'].fillna(0).astype(int).astype(str)
df_ficha_marcas['cod_ibge'] = link+df_ficha_marcas['cod_ibge'].fillna(0).astype(int).astype(str)
#df_insumos['cod_ibge'] = link+df_insumos['cod_ibge'].fillna(0).astype(int).astype(str)
# link is the column with hyperlinks
df_ficha['cod_ibge'] = df_ficha['cod_ibge'].apply(make_clickable)
df_ficha_marcas['cod_ibge'] = df_ficha_marcas['cod_ibge'].apply(make_clickable)
#df_insumos['cod_ibge'] = df_insumos['cod_ibge'].apply(make_clickable)



lista_opcoes = ['insumo', 'composicao', 'insumos_composicao', 'ficha_especificacao', 'ficha_especificacao_com_marcas']



def tabela_tipo_sinapi(tipo_busca):
    if tipo_busca == 'insumo':
        df_consulta = df_insumos.copy()
        coluna = 'DESCRICAO DO INSUMO'
    elif tipo_busca == 'composicao':
        df_consulta = df_composicao.copy()
        coluna = 'DESCRICAO DA COMPOSICAO'
        
    elif tipo_busca == lista_opcoes[2]:
        df_consulta = df[['UNIDADE', 'CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
                          'TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM',
                          'UNIDADE ITEM', 'COEFICIENTE', 'PRECO UNITARIO', 'CUSTO TOTAL',
                          'PRECO UNITARIO com BDI', 'CUSTO TOTAL com BDI']].copy()

#         coluna = 'CODIGO DA COMPOSICAO'
        coluna = 'DESCRICAO DA COMPOSICAO'
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
        #st.write(df_consulta.loc[:, 'DESCRICAO DA COMPOSICAO'].tolist()[0])
        df_consulta = df_consulta.loc[:, :].dropna()

    return df_consulta

df_insumos = transformacao_string_numero(df_insumos.columns[-1], df_insumos)
df = transformacao_string_numero('CUSTO TOTAL', df)
df = transformacao_string_numero('PRECO UNITARIO', df)
df = transformacao_string_numero('COEFICIENTE', df, n=7)
df_composicao = transformacao_string_numero('CUSTO TOTAL', df_composicao)

st.title('SINAPI Janeiro 2022 - Não Desonerado')
st.write('Taxa de BDI atual é ' + str(BDI)+'%')

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
#st.table(df_busca.dropna(thresh=3).reset_index(drop=True))  # , 2000, 400)

link_google = 'https://www.google.com/search?q='+'+'.join(palavras.split(' '))+'&tbm=shop'
st.markdown(link_google)
# st.write("check out this [link](https://share.streamlit.io/mesmith027/streamlit_webapps/main/MC_pi/streamlit_app.py)")


if tipo_busca == lista_opcoes[2]:
    for composicao in df_busca.loc[:, 'DESCRICAO DA COMPOSICAO'].unique().tolist():
        codigo_composicao = df_busca.loc[df_busca['DESCRICAO DA COMPOSICAO']==composicao, 'CODIGO DA COMPOSICAO'].tolist()[0]
        unidade_composicao = df_busca.loc[df_busca['DESCRICAO DA COMPOSICAO']==composicao, 'UNIDADE'].tolist()[0]
        st.write('____________________')
        st.write(' ')
        st.write('**'+ str(codigo_composicao) + ' - '+composicao+ ' ('+unidade_composicao+ ') '+'**')
        st.write(' ')
        df_temp = df_busca.loc[df_busca['DESCRICAO DA COMPOSICAO']==composicao, df_busca.columns[3:]]
        dataframe_show = df_temp.reset_index(drop=True).to_html(escape=False, index=False)
        st.write(dataframe_show, unsafe_allow_html=True)

else:
    dataframe_show= df_busca.reset_index(drop=True).to_html(escape=False, index=False)
    st.write(dataframe_show, unsafe_allow_html=True)

#----------------------------------------------------------------------------------------------------------------------------
# import pandas as pd
# import unicodedata
# import streamlit as st

# st.set_page_config(layout="wide")

# file = 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202111_Desonerado.csv'
# file_insumos_ficha = 'Arquivos A a Z.csv'
# file_insumos_ficha_marcas = 'Arquivos A a Z_com_marcas.csv'

# df = pd.read_csv(file)
# df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM',
#                                                   'CODIGO DA COMPOSICAO']].fillna(0) \
#     .astype(dtype=int)  # , errors = 'ignore')

# df_ficha = pd.read_csv(file_insumos_ficha)
# df_ficha_marcas = pd.read_csv(file_insumos_ficha_marcas)

# df_insumos = df.loc[df['TIPO ITEM'] == 'INSUMO',
#                     ['TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM',
#                      'UNIDADE ITEM', 'PRECO UNITARIO']] \
#     .drop_duplicates()  # ,'CUSTO TOTAL']]

# df_composicao = df[['CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
#                     'UNIDADE', 'CUSTO TOTAL']].drop_duplicates().copy()

# lista_opcoes = ['insumo', 'composicao', 'insumos_composicao', 'ficha_especificacao', 'ficha_especificacao_com_marcas']


# def tabela_tipo_sinapi(tipo_busca):
#     if tipo_busca == 'insumo':
#         df_consulta = df_insumos.copy()
#         coluna = 'DESCRIÇÃO ITEM'
#     elif tipo_busca == 'composicao':
#         df_consulta = df_composicao.copy()
#         coluna = 'DESCRICAO DA COMPOSICAO'
#     elif tipo_busca == lista_opcoes[2]:
#         df_consulta = df[['CODIGO DA COMPOSICAO', 'DESCRICAO DA COMPOSICAO',
#                           'TIPO ITEM', 'CODIGO ITEM', 'DESCRIÇÃO ITEM',
#                           'UNIDADE ITEM', 'PRECO UNITARIO']].copy()

#         coluna = 'CODIGO DA COMPOSICAO'
#     elif tipo_busca == lista_opcoes[3]:
#         df_consulta = df_ficha[df_ficha.columns[1:]]
#         coluna = 'Descrição Básica'
#     elif tipo_busca == lista_opcoes[4]:
#         df_consulta = df_ficha_marcas[df_ficha_marcas.columns[1:]]
#         coluna = 'Referencial / Parâmetro de Pesquisa'

#     return df_consulta, coluna

# def busca_sinapi(palavras, tipo_busca, coluna, df_consulta, lista_palavras):
#     if all(flag == '' for (flag) in lista_palavras):
#         for palavra in palavras.split(' '):
#             #
#             df_consulta = df_consulta[df_consulta[coluna].astype(str) \
#                 .astype(str).str.lower() \
#                 .str.normalize('NFKD') \
#                 .str.encode('ascii', errors='ignore') \
#                 .str.decode('utf-8') \
#                 .str.contains(palavra.lower())].copy()
#             # else:
#             #
#             #     st.write(palavra)


#     else:
#         for palavras_cj, coluna in zip(lista_palavras, df_consulta.columns):
#             for palavra in palavras_cj.split(' '):

#                 df_consulta = df_consulta[df_consulta[coluna]\
#                     .astype(str)\
#                     .astype(str).str.lower() \
#                     .str.normalize('NFKD') \
#                     .str.encode('ascii', errors='ignore') \
#                     .str.decode('utf-8') \
#                     .str.contains(palavra.lower())].copy()

#     if tipo_busca == lista_opcoes[2]:
#         st.write(df_consulta.loc[:, 'DESCRICAO DA COMPOSICAO'].tolist()[0])
#         df_consulta = df_consulta.loc[:, df_consulta.columns[2:]].dropna()

#     return df_consulta

# st.title('SINAPI Novembro 2021 - Desonerado')

# tipo_busca = st.radio('Tipo de busca', lista_opcoes, 0)

# df_busca_, coluna = tabela_tipo_sinapi(tipo_busca)

# palavras = st.text_input('Busca por palavras ou número de composição se "insumos_composicao"')
# palavras = unicodedata.normalize('NFKD', palavras).encode('ascii', 'ignore').decode("utf-8")

# lista_palavras = []
# with st.expander("Busca Avançada"):
#     # st.text(df_busca_.columns)
#     # tipo_busca_avancada = st.checkbox('Busca Avançada')
#     nomes_colunas = df_busca_.columns
#     n_colunas = len(nomes_colunas)
#     cols = st.columns(n_colunas)
#     for nome, col in zip(nomes_colunas, cols):
#         lista_palavras.append(col.text_input(nome))

# # st.text(lista_palavras)

# df_busca = busca_sinapi(palavras, tipo_busca, coluna, df_busca_, lista_palavras)

# # set_option('display. max_colwidth', -1)
# st.table(df_busca.dropna(thresh=3).reset_index(drop=True))  # , 2000, 400)





# # #http://www.sinapi.ibge.gov.br/Catalogo_Insumos/Imprimir_Catalogo/?cod_ibge=7005

# # import pandas as pd
# # import unicodedata
# # import streamlit as st

# # st.set_page_config(layout="wide")


# # file = 'SINAPI_Custo_Ref_Composicoes_Analitico_SC_202111_Desonerado.csv'
# # file_insumos_ficha = 'Arquivos A a Z.csv'
# # file_insumos_ficha_marcas = 'Arquivos A a Z_com_marcas.csv'

# # df = pd.read_csv(file)
# # df[['CODIGO ITEM', 'CODIGO DA COMPOSICAO']] = df[['CODIGO ITEM',
# #                                                   'CODIGO DA COMPOSICAO']].fillna(0)\
# #                                                     .astype(dtype = int)#, errors = 'ignore')

# # df_ficha = pd.read_csv(file_insumos_ficha)
# # df_ficha_marcas = pd.read_csv(file_insumos_ficha_marcas)

# # df_insumos = df.loc[df['TIPO ITEM']=='INSUMO',
# #                     ['TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM',
# #                      'UNIDADE ITEM','PRECO UNITARIO']]\
# #                         .drop_duplicates()#,'CUSTO TOTAL']]

# # df_composicao = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO',
# #                     'UNIDADE','CUSTO TOTAL']].drop_duplicates().copy()



# # st.title('SINAPI Novembro 2021 - Desonerado')

# # lista_opcoes = ['insumo', 'composicao', 'insumos_composicao', 'ficha_especificacao', 'ficha_especificacao_com_marcas']
# # tipo_busca = st.radio('Tipo de busca', lista_opcoes,0)
# # palavras = st.text_input('Busca por palavras ou número de composição se "insumos_composicao"')
# # palavras = unicodedata.normalize('NFKD', palavras).encode('ascii','ignore').decode("utf-8") 


# # def busca_sinapi(palavras, tipo_busca):
# #     if tipo_busca=='insumo':
# #         df_consulta = df_insumos.copy()
# #         coluna = 'DESCRIÇÃO ITEM'
# #     elif tipo_busca=='composicao':
# #         df_consulta = df_composicao.copy()
# #         coluna = 'DESCRICAO DA COMPOSICAO'
# #     elif tipo_busca==lista_opcoes[2]:
# #         df_consulta = df[['CODIGO DA COMPOSICAO','DESCRICAO DA COMPOSICAO',
# #                           'TIPO ITEM','CODIGO ITEM', 'DESCRIÇÃO ITEM',
# #                           'UNIDADE ITEM','PRECO UNITARIO']].copy()

# #         coluna = 'CODIGO DA COMPOSICAO'
# #     elif tipo_busca==lista_opcoes[3]:
# #         df_consulta = df_ficha[df_ficha.columns[1:]]
# #         coluna='Descrição Básica'
# #     elif tipo_busca==lista_opcoes[4]:
# #         df_consulta = df_ficha_marcas[df_ficha_marcas.columns[1:]]
# #         coluna='Referencial / Parâmetro de Pesquisa'
     
# #     for palavra in palavras.split(' '):
# #         if tipo_busca!=lista_opcoes[2]:
# #             df_consulta = df_consulta[df_consulta[coluna]\
# #                 .astype(str).str.lower()\
# #                 .str.normalize('NFKD')\
# #                 .str.encode('ascii', errors='ignore')\
# #                 .str.decode('utf-8')\
# #                 .str.contains(palavra.lower())].copy()
# #         else:
            

# #             st.write(palavra)             
# #             st.write(df_consulta.loc[df_consulta[coluna]==int(palavras), 'DESCRICAO DA COMPOSICAO'].tolist()[0])
# #             df_consulta =df_consulta.loc[df_consulta[coluna]==int(palavras), df_consulta.columns[2:]].dropna()
    
    
# #     return df_consulta

# # df_busca = busca_sinapi(palavras, tipo_busca)

# # #set_option('display. max_colwidth', -1)
# # st.table(df_busca.dropna(thresh=3).reset_index(drop=True))#, 2000, 400)
