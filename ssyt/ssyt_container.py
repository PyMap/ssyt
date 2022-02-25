import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import orca

from vivienda import *
from contexto_urbano import *
from mobilidad import *
from accesibilidad import *
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


menu_list = st.sidebar.radio('Secciones', ["Inicio", "Condiciones habitacionales", "Mercado de alquileres", "Mobilidad urbana", "Accesibilidad"])

if menu_list == "Inicio":

    col1, _ ,col3 = st.columns((2,0.5,2))

    col1.header("SSyT - Sociedad y Territorio")

    col1.markdown("""
                ```
                > Llamamos Sistema SyT a un conjunto de herramientas diseñadas para
                analizar y estudiar las dinámicas urbanas de un área metropolitana.
                Para explorar cómo se comportan y cuáles son sus  peculiaridades se
                propone un abordaje ordenado a través de componentes específicos.\n

                Cada uno de ellos facilita un visor de resultados donde se pueden
                consultar las métricas principales de las dinámicas estudiadas.
                Este demo se concentra en el área metropolitana de Buenos Aires
                y contiene sólo algunos componentes a modo de ejemplo. El marco de
                trabajo es lo suficientemente flexible como para definir nuevos
                componentes, reemplazar los existentes o cambiar la región
                de análisis.
                ```
    """)

    landing = Image.open('./img/silueta_urbana.jpg')
    col3.image(landing, width=450)

    st.subheader('** Componentes de análisis**')
    st.markdown("""

    * **Condiciones habitacionales**:
        ```
        - esta seccion permite estudiar la distribución territorial de un conjunto de variables censales. Todas ellas, vinculadas
        a las características de las viviendas y ubicación en el espacio. Se proponen índices simples y complejos para su estudio.
        Las fuentes de información principal son el CNPHV - 2010 y el Precenso de Viviendas del INDEC.
        ```

    * **Mercado de alquileres**:
        ```
        - esta seccion permite estudiar la evolución de precios de viviendas del mercado formal de alquileres. La misma se construye
          en base al conjunto de datos disponibilizado por Properati y ajusta precios por inflación en base al IPC/INDEC ICL/BCR.
        ```

    * **Informalidad urbana**:
        ```
        - definir
        ```
    """)


elif menu_list == "Condiciones habitacionales":
    st.subheader('Visor de patrones de asentamiento')
    st.markdown('Seleccione una variable censal para analizar su distribución en la región deseada')
    st.markdown(' ')

    col1, col2, col3, col4 = st.columns((1,1,1,1))
    regions = ['Capital Federal', 'Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte', 'Bs.As. G.B.A. Zona Sur']
    region = col1.selectbox('Region', regions)

    indicators = ['Calidad constructiva de la vivienda', 'Calidad de conexiones a servicios básicos',
                  'Viviendas en construcción', 'Viviendas en altura', 'Viviendas en áreas de difícil acceso']
    indicator = col2.selectbox('Indicador', indicators)

    if indicator == 'Calidad constructiva de la vivienda':
        with st.expander("Inspeccionar indicador"):
         st.write("""
             Según el Censo 2010, la calidad de la vivienda se encuentra determinada por dos tipos de materiales: los predominantes
             en los pisos y cubierta exterior de sus techos. Así, el indicador se estructura en cuatro calidades (para una lectura más
             detallada sobre las mismas se puede consultar la [siguiente documentación](https://www.indec.gob.ar/ftp/cuadros/poblacion/informe_calmat_2001_2010.pdf).
             El indicador propuesto agrupa las calidades III y IV como irrecuperables y mantiene las I y II como aceptables y recuperables respectivamente.
             Para el análisis de distribución territorial, se utiliza el [índice de Duncan](https://www.scielo.cl/scielo.php?script=sci_arttext&pid=S0250-71612006000300004)
             (comunmente utilizado en el estudio de segregación territorial).
             Este describe la manera en la que se distribuye un grupo en el espacio a partir de la relación entre distintos niveles administrativos
             (uno de mayor y otro de menor agregación). El mismo varía entre cero y uno indicando distribuciones igualitarias o de máxima concentración.
             El valor cero sólo se alcanza cuando en todas las unidades hay la misma proporción entre el grupo estudiado y el resto de población.
         """)

    if (indicator == 'Calidad constructiva de la vivienda') and (region == 'Capital Federal'):

        area_superior = col3.selectbox('Area superior', ['barrio','comuna'])
        categoria_inmat = col4.selectbox('Categoría', ['recuperables', 'irrecuperables', 'aceptables'])

        radios_geom = radios_caba_2010()
        radios_vals = inmat_radios_caba_2010()

    elif (indicator == 'Calidad constructiva de la vivienda') and (region != 'Capital Federal'):

        area_superior = col3.selectbox('Area superior', ['departamento'])
        categoria_inmat = col4.selectbox('Categoría', ['aceptables', 'recuperables', 'irrecuperables'])
        radios_geom = radios_gba24_2010().to_crs(4326)
        radios_vals = inmat_radios_gba24_2010()

    else:
        pass

    inmat_inf = radios_inmat_2010(region_name=region, geog=radios_geom, vals=radios_vals)

    col5, col6 = st.columns((1,1))
    fig1 = construye_territorio(gdf=inmat_inf, nombre_unidad_s=area_superior, nombre_unidad_i='str_link',
                                nombre_variable='total_inmat', nombre_categoria=categoria_inmat, estadistico='CEC', tipo='bar', dinamico=True)

    fig2 = construye_territorio(gdf=inmat_inf, nombre_unidad_s=area_superior, nombre_unidad_i='str_link',
                                nombre_variable='total_inmat', nombre_categoria=categoria_inmat, estadistico='CEC', tipo='scatter', dinamico=True)

    col5.plotly_chart(fig1, use_container_width=True)
    col6.plotly_chart(fig2, use_container_width=True)

    territorio_superior = construye_territorio(gdf=inmat_inf, nombre_unidad_s=area_superior, nombre_unidad_i='str_link',
                                               nombre_variable='total_inmat', nombre_categoria=categoria_inmat, estadistico=None, tipo=None)

    inmat_sup = indice_geografia_superior(territorio_df=territorio_superior, nombre_area=area_superior, nombre_region=region)
    fig3 = plot_folium_dual_choroplet(gdf_inferior=inmat_inf, gdf_superior=inmat_sup, categoria=categoria_inmat,
                                      indicador_superior='CEC', nombre_superior=area_superior, nombre_region=region)
    folium_static(fig3, width=1350, height=500)

elif menu_list == "Mercado de alquileres":
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

elif menu_list == "Mobilidad urbana":

    st.subheader('Visor de mobilidad')
    st.markdown('Seleccione un punto de referencia sobre el mapa para generar una red de calles.')
    st.markdown(' ')

    network_types = ["all_private", "all", "bike", "drive", "drive_service", "walk"]
    connectivity_stats = ['Node degree', 'Degree centrality', 'Betweenness centrality']

    col1, col2, col3, _, col4, col5 = st.columns((0.35, 0.45, 0.5, 0.05, 0.8, 0.75))
    col6, col7 = st.columns(2)

    selected_network_type = col1.selectbox('Tipo de red', network_types, index=5)
    selected_stats = col2.selectbox('Métrica de conectividad', connectivity_stats, index=0)
    buffer_dist = col3.number_input('Indique buffer de distancia (mts)', min_value=300)

    if 'ref' in orca.list_injectables():
        ref = orca.get_injectable('ref')
    else:
        # use a default reference point
        ref = (-34.50944, -58.58610)

    G = build_street_network(selected_network_type, ref, buffer_dist)

    if selected_stats == 'Node degree':
        network_metric = node_degree(G)
    elif selected_stats == 'Degree centrality':
        network_metric = degree_centrality(G)
    elif selected_stats == 'Betweenness centrality':
            network_metric = betweenness_centrality(G, selected_network_type)
    else:
        print('Add other supported network stats')

    colors = {'Betweenness centrality':'plasma',
              'Degree centrality':'viridis',
              'Node degree':'YlOrRd'}

    # set ordinal idx for shortest path routing nodes recognition
    counter = 1
    for n in G.nodes(data=True):
        n[1]['ordinal_idx'] = counter
        counter += 1

    # node attributes
    fig1 = plot_nodes_folium(G, attr_name=selected_stats, palette=colors[selected_stats])
    fig1.add_child(folium.LatLngPopup())

    with col6:
        mapdata = st_folium(fig1, width=625, height=500)

    if mapdata is not None:
        print(mapdata['last_clicked'])
        # interacts with the map and generates new reference
        if mapdata['last_clicked'] is not None:
            lat_click = mapdata['last_clicked']['lat']
            lng_click = mapdata['last_clicked']['lng']
            ref = (lat_click, lng_click)
            orca.add_injectable('ref', ref)
        else:
            informative_print = ''
            st.write(informative_print)

    # map ordinal idx to osmn id
    ordinal_idx_to_osmnidx = {}
    for n in G.nodes(data=True):
        ordinal_idx_to_osmnidx[n[1]['ordinal_idx']] = n[0]

    first_node = list(ordinal_idx_to_osmnidx.keys())[0]
    last_node = list(ordinal_idx_to_osmnidx.keys())[-1]

    origin = col4.number_input('Origen', value=first_node)
    destin = col5.number_input('Destino', value=last_node)

    route = nx.shortest_path(G, ordinal_idx_to_osmnidx[origin], ordinal_idx_to_osmnidx[destin])

    # shortest path routing
    with col7:
        fig2 = ox.folium.plot_route_folium(G,route, color='red')
        folium_static(fig2, width=625, height=490)

    definitions = {
                   'Node degree':'El grado de un nodo indica la cantidad de ejes o calles adyacentes al nodo.',
                   'Degree centrality':'''El grado de centralidad (o degree centrality) de un nodo computa la cantidad
                                        de conexiones del nodo normalizada por el total de nodos dentro de la red. Así,
                                        dicha métrica indica el porcentage de conexiones actual sobre el máximo posible.''',
                   'Betweenness centrality':'''La centralidad de intermediación, o simplemente intermediación
                                            (en inglés, betweenness) es una medida de centralidad
                                            que cuantifica el número de veces que un nodo se encuentra entre los
                                            caminos más cortos de la red. Un nodo tendrá una alta intermediación si
                                            se encuentra presente en un elevedado porcentage de los mismos.''',
                   }
    with st.expander("Inspeccionar indicador"):
     st.write('{}'.format(definitions[selected_stats]))

elif menu_list == "Accesibilidad":
    st.subheader('Visor de accesibilidad')
    st.markdown('''Indique el lugar donde desea construir una red de calles y cliquee sobre
                   el mapa para obtener un punto de referencia al que se calcularán los tiempos de viaje
                   para todos los nodos de la red.''')
    st.markdown(' ')

    col1, col2, col3 = st.columns(3)
    default_place= 'Villa Hidalgo, José León Suárez, Partido de General San Martín, Buenos Aires'
    place = col1.text_input(label='Ingresar nombre del sitio', value=default_place)

    network_types = ["all_private", "all", "bike", "drive", "drive_service", "walk"]
    selected_network_type = col2.selectbox('Tipo de red', network_types, index=5)
    travel_speed = col3.number_input('Indique la velocidad de viaje (en km/h)', min_value=4)


    G = build_graph_by_name(place, network_type=selected_network_type)
    kwargs = {'weight' : '0.75', 'color': 'grey'}
    fig1 = ox.plot_graph_folium(G, tiles='openstreetmap',  **kwargs)
    fig1.add_child(folium.LatLngPopup())

    # nodes
    fig2 = plot_simple_nodes_folium(G, m=fig1, node_color='red')

    col4, col5 = st.columns(2)

    with col4:
        mapdata = st_folium(fig1, width=625, height=500)

    if mapdata is not None:
        print(mapdata['last_clicked'])
        # interacts with the map and generates new reference
        if mapdata['last_clicked'] is not None:
            lat_click = mapdata['last_clicked']['lat']
            lng_click = mapdata['last_clicked']['lng']
            ref = (lat_click, lng_click)

            with col5:
                fig3 = ox.plot_graph_folium(G, tiles='cartodbdark_matter',  **kwargs)
                fig4 = plot_isochrone(G, ref, travel_speed, m=fig3)
                slat = mapdata['bounds']['_southWest']['lat']
                slon = mapdata['bounds']['_southWest']['lng']
                nlat = mapdata['bounds']['_northEast']['lat']
                nlon = mapdata['bounds']['_northEast']['lng']
                fig4.fit_bounds([(slat, slon), (nlat, nlon)])
                folium_static(fig4, width=625, height=490)
