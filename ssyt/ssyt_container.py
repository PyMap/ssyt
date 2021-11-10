import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from visprev import *

st.set_page_config(
page_title="Systema SYT",
layout='wide',
initial_sidebar_state='collapsed')

st.write(
        """
<iframe src="resources/sidebar-closer.html" height=0 width=0>
</iframe>""",
        unsafe_allow_html=True,
    )

menu_list = st.sidebar.radio('Go to', ["INICIO", "SSYT", "VISPAE", "VISPREV", "VISMYA"])

if menu_list == "INICIO":
    landing = Image.open('./img/urban_shapes.png')
    st.image(landing, width=700)
    st.header("CEEU - Systema Sociedad y Territorio")
    st.markdown(
        """
        Las formas de las ciudades, tanto si han sido pensadas específicamente como si son el resultado más o menos espontáneo
        de dinámicas diferentes, cristalizan y \n
        reflejan las lógicas de las sociedades que acogen (Ascher Francois, 2004: p20 ). \n

        ```
        Llamamos Sistema SYT a un conjunto de herramientas diseñadas para analizar y estudiar los principales componentes de las dinámicas \n
        urbanas de un área metropolitana. La manera en la que la población transita y habita en el espacio de un territorio constituyen, entre otros**, \n
        eventos determinantes  en la forma de una ciudad. Explorar cómo se comportan y cuáles son sus  peculiaridades de un modo ordenado y a través de componentes \n
        específicos es el objetivo principal de este proyecto.
        ```""")

elif menu_list == "VISPREV":
    st.subheader('**_Parametros de la consulta_**')

    col1, col2, col3, col4, col5 = st.columns(5)

    year = col1.selectbox('Año', ['2015','2016','2017','2018','2019','2020','2021'])

    months = ['01','02','03',
              '04','05','06',
              '07','08','09',
              '10','11','12']

    first_month = col2.selectbox('Mes de inicio', months)
    last_month = col3.selectbox('Mes de finalización', months)
    df = get_properati_data(year, first_month, last_month)

    region = col4.selectbox('Region', ['Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte',
                                       'Capital Federal', 'Bs.As. G.B.A. Zona Sur'])
    series = choose_jurisdiction(df, region)
    
    deflactor = col5.selectbox('Deflactor', ['IPC Indec', 'ICL BCRA'])
    if deflactor == 'IPC Indec':
        ipc_indec = read_ipc()
        # SE PODRIA CONSUMIR DESDE LA API CKAN
        salarios = pd.read_csv('https://storage.googleapis.com/ssyt/data/indice-salarios-periodicidad-mensual-base-octubre-2016.csv')
        construye_d_val = True
        d_val = None

    else:
        print('ADD CSV ICL BCRA')
        ipc_indec = None
        salarios = None
        construye_d_val = True
        d_val = read_icl()

    region_summary = series.apply(lambda x: deflactar_serie(pe=x.period,
                                                            pr=x.price,
                                                            ba='2020-3',
                                                            construye_d=construye_d_val,
                                                            ipc=ipc_indec,
                                                            isa=salarios,
                                                            rubro_ipc='Alquiler de la vivienda',
                                                            d=d_val),
                                                            axis=1)

    adjusted_region = region_summary.apply(pd.Series)
    region_columns = ['periodo', 'precio_nom', 'coeficiente', 'ipc_base', 'ipc_per', 'precio_con']
    adjusted_region.columns = region_columns

    def plot_prices(df):
        unit = 1/plt.rcParams['figure.dpi']
        width,height = 800,  300
        fig, ax = plt.subplots(figsize=(width*unit, height*unit))
        df.set_index('periodo')['precio_nom'].plot(kind='line', grid=True, color='r')
        df.set_index('periodo')['precio_con'].plot(kind='line', grid=True, color='b')
        return fig

    container = st.container()
    container.write(adjusted_region)

    st.write(plot_prices(df=adjusted_region))
