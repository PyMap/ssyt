import streamlit as st
import pandas as pd
import geopandas as gpd
import orca

from vivienda import *
from poblacion import *
from datasources import *
from charts import *
from utils import *


st.set_page_config(
    page_title="Systema SyT",
    page_icon="./sl//favicon.ico",
    layout='wide',
    initial_sidebar_state='collapsed')

st.write(
        """
<iframe src="resources/sidebar-closer.html" height=0 width=0>
</iframe>""",
        unsafe_allow_html=True,
    )

# CSS
with open('./sl/style.css') as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


menu_list = st.sidebar.radio('Secciones', ["Inicio", "SSyT", "Vivienda", "Poblacion", "Accesibilidad"])

if menu_list == "Inicio":
    landing = Image.open('./img/urban_shapes.png')
    st.image(landing, width=700)
    st.header("CEEU - Systema Sociedad y Territorio")
    st.markdown(
        """
        _Las formas de las ciudades, tanto si han sido pensadas específicamente como si son el resultado más o menos espontáneo
        de dinámicas diferentes, cristalizan y reflejan las lógicas de las sociedades que acogen (Ascher Francois, 2004: p20 )._
        """)

    st.markdown(" ")
    st.markdown("""
                ```
                Llamamos Sistema SYT a un conjunto de herramientas diseñadas para analizar y estudiar \n
                los principales componentes de las dinámicas urbanas de un área metropolitana. La manera en la que la población transita y habita \n
                en el espacio de un territorio constituyen, entre otros, eventos determinantes  \n
                en la forma de una ciudad. Explorar cómo se comportan y cuáles son sus  peculiaridades de un modo ordenado y a través de componentes \n
                específicos es el objetivo principal de este proyecto.
                ```
    """)
elif menu_list == "SSyT":
    st.markdown("""

    * Vivienda: esta seccion permite estudiar la evolución de precios de viviendas del mercado formal de alquileres. La misma se construye
    en base al conjunto de datos disponibilizado por Properati y ajusta precios por inflación en base al IPC/INDEC ICL/BCR.

    * Poblacion: esta seccion permite estudiar la distribución territorial de un conjunto de variables censales ...
    * Movilidad: esta seccion (OSMNx/grafos)

    """)
elif menu_list == "Vivienda":
    st.subheader('Visor de precios de alquiler')
    st.markdown('Seleccione el período de análisis y el tipo de deflactor para analizar la evolución de precios en la región deseada')
    st.markdown(' ')

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns((1,1,1,1,2,2,1,2))
    selection_year = ['2015','2016','2017','2018','2019','2020','2021'] # to use 2015/2016 see Issue #7
    first_year = col1.selectbox('Año inicio', selection_year[2:], index=3)
    last_year = col2.selectbox('Año fin', selection_year[2:], index=4)

    months = ['01','02','03',
              '04','05','06',
              '07','08','09',
              '10','11','12']

    first_month = col3.selectbox('Mes inicio', months, index=6)
    last_month = col4.selectbox('Mes fin', months, index=11)
    df = get_properati_data(first_year, last_year, first_month, last_month)

    regions = ['Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte',
               'Capital Federal', 'Bs.As. G.B.A. Zona Sur']
    region = col5.selectbox('Region', regions)
    orca.add_injectable('selected_region', region)
    series = choose_jurisdiction(df, region)

    deflactor = col6.selectbox('Deflactor', ['IPC Indec', 'ICL BCRA'])
    periodo_base = col7.radio( "Mes base", ('2020-7', '2020-3'))

    if deflactor == 'IPC Indec':
        ipc_indec = read_ipc()
        nombre_rubro = col8.selectbox('Rubro IPC', ipc_indec['Región GBA'].unique(), index=0)
        # SE PODRIA CONSUMIR DESDE LA API CKAN
        salarios = get_wages()
        construye_d_val = True
        d_val = None

    else:
        print('ADD CSV ICL BCRA')
        ipc_indec = None
        salarios = None
        construye_d_val = False
        d_val = read_icl()
        nombre_rubro = None

    region_summary = series.apply(lambda x: deflactar_serie(pe=x.period,
                                                            pr=x.price,
                                                            ba=periodo_base,
                                                            construye_d=construye_d_val,
                                                            ipc=ipc_indec,
                                                            isa=salarios,
                                                            rubro_ipc=nombre_rubro,
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
    fig2 = plotly_percent_change(df=adjusted_region, index_name=deflactor, move_legend=True)

    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1,use_container_width = True)
    col2.plotly_chart(fig2,use_container_width = True)

    with st.expander("Inspeccionar ajuste de precios"):
     st.write("""
         La tabla que se presenta a continuación detalla la tranformación
         realizada por el índice y el período base seleccionados en el menú.
     """)
     st.write(adjust_prices_by_inflation_table(df=adjusted_region, index_name=deflactor, base=periodo_base))

    col3 = st.container()
    col4, col5 = st.columns((2,2))
    previous_names = orca.list_tables()

    tables = []
    for n in previous_names:
        t= orca.get_table(n).to_frame()
        tables.append(t)
    compare_against_previous = pd.concat(tables)

    fig3 = plotly_prices(df=compare_against_previous, compare=True, move_legend=False)
    col3.plotly_chart(fig3, use_container_width=True)

    if region == 'Capital Federal':
        prices_over_time = nominal_prices_over_time_caba()
        offer_df = caba_rents_offer()
        base_polygons = caba_neighborhood_limits()
    elif region ==  'Bs.As. G.B.A. Zona Oeste':
        prices_over_time = nominal_prices_over_time_gba_oeste()
        offer_df = gba_oeste_rents_offer()
        base_polygons = gba_oeste_dept_limits()
    elif region == 'Bs.As. G.B.A. Zona Norte':
        prices_over_time = nominal_prices_over_time_gba_norte()
        offer_df = gba_norte_rents_offer()
        base_polygons = gba_norte_dept_limits()
    elif region == 'Bs.As. G.B.A. Zona Sur':
        prices_over_time = nominal_prices_over_time_gba_sur()
        offer_df = gba_sur_rents_offer()
        base_polygons = gba_sur_dept_limits()
    else:
        pass
    filtered_points = filter_data_on_period(prices_over_time, first_year, first_month, last_year, last_month)
    filtered_points['period'] = filtered_points['periodo'].apply(lambda x: reformat_period(x))

    points_summary = filtered_points.apply(lambda x: deflactar_serie(pe=x.period,
                                                                     pr=x.monto,
                                                                     ba=periodo_base,
                                                                     construye_d=construye_d_val,
                                                                     ipc=ipc_indec,
                                                                     isa=salarios,
                                                                     rubro_ipc=nombre_rubro,
                                                                     d=d_val),
                                                                     axis=1)

    adjusted_points = points_summary.apply(pd.Series)
    points_columns = ['periodo', 'precio_nom', 'coeficiente', 'indice_base', 'indice_per', 'precio_con']
    adjusted_points.columns = points_columns
    filtered_points['$ constantes'] = adjusted_points['precio_con'].astype(int)
    filtered_points['$ nominales'] = adjusted_points['precio_nom'].astype(int)

    fig4 = plot_graduated_scattermap(points_gdf=filtered_points, polygons_gdf=base_polygons, indicator='$ constantes')
    col4.plotly_chart(fig4, use_container_width=True)

    filtered_offer = filter_data_on_period(offer_df, first_year, first_month, last_year, last_month)
    fig5 = plot_density_scatter_map(points_df=filtered_offer, polygons_gdf=base_polygons)
    col5.plotly_chart(fig5, use_container_width=True)

elif menu_list == "Poblacion":
    radios_inmat = gpd.read_file('https://storage.googleapis.com/python_mdg/carto_cursos/radios_inmat.zip')
    # renombramos algunas columnas
    radios_inmat.rename(columns= {'acept':'aceptables',
                                  'reup':'recuperables',
                                  'irrecup':'irrecuperables'}, inplace=True)

    # podemos ver el índice de concentración para otra categoría de viviendas por barrio
    st.write(construye_territorio(gdf=radios_inmat, nombre_unidad_s='COMUNA', nombre_unidad_i='RADIO_I',
                                  nombre_variable='VIVIEND', nombre_categoria='recuperables', estadistico=None, tipo=None))

    st.write(construye_territorio(gdf=radios_inmat, nombre_unidad_s='COMUNA', nombre_unidad_i='RADIO_I',
                                  nombre_variable='VIVIEND', nombre_categoria='recuperables', estadistico='CEC', tipo='bar'))

    st.write(construye_territorio(gdf=radios_inmat, nombre_unidad_s='COMUNA', nombre_unidad_i='RADIO_I',
                                  nombre_variable='VIVIEND', nombre_categoria='recuperables', estadistico='CEC', tipo='scatter'))
