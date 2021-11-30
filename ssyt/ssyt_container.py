import streamlit as st
import pandas as pd
import geopandas as gpd
import orca

from visprev import *
from charts import *

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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    first_year = col1.selectbox('Año de inicio', ['2015','2016','2017','2018','2019','2020','2021'])
    last_year = col2.selectbox('Año de finalización', ['2015','2016','2017','2018','2019','2020','2021'])

    months = ['01','02','03',
              '04','05','06',
              '07','08','09',
              '10','11','12']

    first_month = col3.selectbox('Mes de inicio', months)
    last_month = col4.selectbox('Mes de finalización', months)
    df = get_properati_data(first_year, last_year, first_month, last_month)

    regions = ['Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte',
               'Capital Federal', 'Bs.As. G.B.A. Zona Sur']
    region = col5.selectbox('Region', regions)
    orca.add_injectable('selected_region', region)
    series = choose_jurisdiction(df, region)

    deflactor = col6.selectbox('Deflactor', ['IPC Indec', 'ICL BCRA'])
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
    region_columns = ['periodo', 'precio_nom', 'coeficiente', 'indice_base', 'indice_per', 'precio_con']
    adjusted_region.columns = region_columns

    selected_region = orca.get_injectable('selected_region')
    adjusted_region['region'] = selected_region
    table_name = 'selected_{}'.format(selected_region)
    orca.add_table(table_name, adjusted_region)


    container = st.container()
    fig1 = plotly_prices(df=adjusted_region, move_legend=True)
    fig2 = plotly_coeff(df=adjusted_region, move_legend=True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1,use_container_width = True)
    col2.plotly_chart(fig2,use_container_width = True)

    col3 = st.container()
    col4 = st.container()
    previous_names = orca.list_tables()

    tables = []
    for n in previous_names:
        t= orca.get_table(n).to_frame()
        tables.append(t)
    compare_against_previous = pd.concat(tables)

    fig3 = plotly_prices(df=compare_against_previous, compare=True, move_legend=False)
    col3.plotly_chart(fig3, use_container_width=True)

    if region == 'Capital Federal':
        prices_over_time = gpd.read_file('https://storage.googleapis.com/ssyt/data/caba_nominales_012015_072021.zip')
        base_polygons = gpd.read_file('https://storage.googleapis.com/ssyt/data/caba_barrios.zip')
    elif region ==  'Bs.As. G.B.A. Zona Oeste':
        prices_over_time = gpd.read_file('https://storage.googleapis.com/ssyt/data/zoeste_012015_072021.zip')
        base_polygons = gpd.read_file('https://storage.googleapis.com/ssyt/data/zoeste_deptos.zip')
    elif region == 'Bs.As. G.B.A. Zona Norte':
        prices_over_time = gpd.read_file('https://storage.googleapis.com/ssyt/data/znorte_nominales_012015_072021.zip')
        base_polygons = gpd.read_file('https://storage.googleapis.com/ssyt/data/znorte_deptos.zip')
    elif region == 'Bs.As. G.B.A. Zona Sur':
        prices_over_time = gpd.read_file('https://storage.googleapis.com/ssyt/data/zsur_nominales_012015_072021.zip')
        base_polygons = gpd.read_file('https://storage.googleapis.com/ssyt/data/zsur_deptos.zip')
    else:
        pass
    filtered_points = filter_data_on_period(prices_over_time, first_year, first_month, last_year, last_month)

    fig4 = plot_graduated_scattermap(points_gdf=filtered_points, polygons_gdf=base_polygons, indicator='monto')
    col4.plotly_chart(fig4, use_container_width=True)
