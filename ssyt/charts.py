import plotly_express as px
import plotly.graph_objects as go
import json
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from utils import *
import folium
from streamlit_folium import folium_static
import mapclassify
from vivienda import formatea_isa


def matplot_prices(df):
    unit = 1/plt.rcParams['figure.dpi']
    width,height = 800,  300
    fig, ax = plt.subplots(figsize=(width*unit, height*unit))
    df.set_index('periodo')['precio_nom'].plot(kind='line', grid=True, color='r')
    df.set_index('periodo')['precio_con'].plot(kind='line', grid=True, color='b')
    return fig

def plotly_prices(df, compare=False, move_legend=False):

    if compare:
        long_df = pd.melt(df, id_vars=['periodo','region'], value_vars=['precio_nom','precio_con'])
        long_df.rename(columns={'variable':'precio'}, inplace=True)
        long_df['precio'].replace({'precio_nom':'nominal', 'precio_con':'constante'}, inplace=True)

        price_colors = {'Bs.As. G.B.A. Zona Oeste':'#A7226E', 'Bs.As. G.B.A. Zona Norte':'#EC2049',
                        'Capital Federal': '#2F9599', 'Bs.As. G.B.A. Zona Sur':'#F7DB4F'}
        long_df = long_df.loc[long_df['precio']=='constante'].copy()

        yaxis_title = "$ ARS (Constantes)"
        fig = px.line(long_df,
                      x= 'periodo',
                      y= 'value',
                      color='region',
                      color_discrete_map=price_colors)

        mean_reference = long_df.groupby('periodo')[['value']].mean().reset_index()
        mean_reference['dt_periodo'] = pd.to_datetime(mean_reference['periodo'],format='%Y-%m')
        sorted_mean_reference = mean_reference.sort_values(by='dt_periodo')

        fig.add_trace(
            go.Scatter(
                x=sorted_mean_reference['periodo'],
                y=sorted_mean_reference['value'],
                mode='lines',
                line = dict(shape = 'linear', color = 'rgb(10, 12, 240)', dash = 'dash'),
                name='promedio regional',
                marker = dict(symbol = "hash", color = 'rgb(17, 157, 255)',size = 12),
                connectgaps = True))
    else:
        long_df = pd.melt(df, id_vars=['periodo'], value_vars=['precio_nom','precio_con'])
        long_df.rename(columns={'variable':'precio'}, inplace=True)
        long_df['precio'].replace({'precio_nom':'nominal', 'precio_con':'constante'}, inplace=True)
        yaxis_title = "$ ARS"
        price_colors = {'nominal': '#0000FF', 'constante': '#EE4B2B'}
        fig = px.line(long_df,
                      x= 'periodo',
                      y= 'value',
                      color='precio',
                      color_discrete_map=price_colors)

    fig.update_layout(autosize=True,
                      width=800,
                      height=350,
                      plot_bgcolor ='white',
                      hoverlabel=dict(bgcolor="white"),
                      yaxis=None,
                      xaxis=None)

    if move_legend:
        fig.update_layout(legend=dict(
                                      orientation="h",
                                      yanchor="bottom",
                                      y=-0.4,
                                      xanchor="right",
                                      x=1
                                     ))

    fig.update_traces(mode='markers+lines', hovertemplate='$ARS: %{y:.2f}')
    fig.update_yaxes(showline=True, linecolor='black', title_text=yaxis_title)
    fig.update_xaxes(showline=True, linecolor='black')

    return fig

def plotly_coeff(df, move_legend=False):

    index_colors = {'variacion periodo': '#F9D71C', 'coeficiente variacion': '#FAFD0F'}

    wide_df = df[['periodo', 'indice_base', 'indice_per', 'coeficiente']].copy()
    wide_df.rename(columns={'indice_base':'indice base',
                            'indice_per':'variacion periodo',
                            'coeficiente': 'coeficiente variacion'}, inplace=True)

    fig = go.Figure(data=[
        go.Bar(name='variabilidad periodo (indice)', x=wide_df['periodo'],
               y=wide_df['variacion periodo'])])
    fig.update_traces(marker_color='#ADD8E6', marker_line_color='#1E3F66',
                  marker_line_width=1.5, opacity=0.6)

    fig.add_trace(
        go.Scatter(
            x=wide_df['periodo'],
            y=wide_df['coeficiente variacion'],
            mode='lines+markers',
            name='coeficiente de variacion',
            marker_color='#000000'))

    fig.update_layout(autosize=True,
                      width=800,
                      height=350,
                      plot_bgcolor ='white',
                      hoverlabel=dict(bgcolor="white"),
                      yaxis=None,
                      xaxis=None)

    if move_legend:
        fig.update_layout(legend=dict(
                                      orientation="h",
                                      yanchor="bottom",
                                      y=-0.4,
                                      xanchor="right",
                                      x=1
                                     ))

    #fig.update_traces(mode='markers+lines', hovertemplate='VAR: %{y:.2f}')
    fig.update_yaxes(showline=True, linecolor='black')
    fig.update_xaxes(showline=True, linecolor='black')

    return fig

def plotly_percent_change(df, index_name, move_legend=False):

    df_ = df[['periodo', 'indice_per', 'precio_con', 'precio_nom']].copy()

    df_.rename(columns={'indice_per':'indice periodo',
                        'precio_nom':'precios_nominales',
                        'precio_con':'precios constantes'}, inplace=True)

    df_['Precios constantes (%)'] = df_['precios constantes'].pct_change() * 100
    df_['Indice de ajuste (%)'] = df_['indice periodo'].pct_change() * 100

    fig = go.Figure(data=[
        go.Bar(name='Evolucion $ARS constantes (%)', x=df_['periodo'],
               y=df_['Precios constantes (%)'],
               hovertemplate="$ARS constantes: %{y:.2f}% <extra></extra>",
               marker={"color": "rgba(240, 240, 240, 1.0)", "line": {"width": 0}}),
               ])

    fig.update_traces(marker_color='#ADD8E6', marker_line_color='#1E3F66',
                      marker_line_width=1.5, opacity=0.6)

    fig.add_trace(
        go.Scatter(
            x=df_['periodo'],
            y=df_['Indice de ajuste (%)'],
            mode='lines+markers',
            name='Evolucion {} (%)'.format(index_name),
            marker_color='#000000',
            hovertemplate = '{}'.format(index_name)+': %{y:.2f}% <extra></extra>'))

    fig.update_layout(autosize=True,
                      width=800,
                      height=350,
                      plot_bgcolor ='white',
                      hoverlabel=dict(bgcolor="white"),
                      yaxis=None,
                      xaxis=None)

    if move_legend:
        fig.update_layout(legend=dict(
                                      orientation="h",
                                      yanchor="bottom",
                                      y=-0.4,
                                      xanchor="right",
                                      x=1,
                                     ))

    fig.update_yaxes(showline=True, linecolor='black', ticksuffix = "%", title='Cambio porcentual')
    fig.update_xaxes(showline=True, linecolor='black')

    return fig


def plotly_trends(df, periodo_base, isa, rubro_isa,  move_legend):

    df_ = df[['periodo', 'indice_per', 'precio_con', 'precio_nom']].copy()
    isa_ = formatea_isa(isa, rubro_isa)
    isa_ =  isa_[isa_.index.isin(df_.periodo.unique())].copy()

    df_.rename(columns={'indice_per':'indice periodo',
                        'precio_nom':'precios_nominales',
                        'precio_con':'Precios constantes ($ARS)'}, inplace=True)
    df_['Indice de salarios'] = isa_.values

    from plotly.subplots import make_subplots
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            name='$ARS constantes - base {} '.format(periodo_base),
            x=df_['periodo'],
            y=df_['Precios constantes ($ARS)'], #agregar año base con el que deflacta
            mode='lines+markers',
            marker_color='#000000',
            #hovertemplate = '{}'.format(index_name)+': %{y:.2f}% <extra></extra>'
            hovertemplate = '$ARS {}'.format(periodo_base)+': %{y:.2f} <extra></extra>'
            ),
            secondary_y=True)

    fig.update_traces(marker_color='#ADD8E6', marker_line_color='#1E3F66',
                      marker_line_width=1.5, opacity=0.6)

    fig.add_trace(
        go.Scatter(
        name='Evolución ISA - base 2016-12 ',
        x=df_['periodo'],
        y=df_['Indice de salarios'],
        hovertemplate="ISA: %{y:.2f}% <extra></extra>",
        marker_color = '#000000'),
        secondary_y=False
    )

    fig.update_layout(autosize=True,
                      width=800,
                      height=350,
                      plot_bgcolor ='white',
                      hoverlabel=dict(bgcolor="white"),
                      yaxis=None,
                      xaxis=None)
    if move_legend:
        fig.update_layout(legend=dict(
                                      orientation="h",
                                      yanchor="bottom",
                                      y=-0.4,
                                      xanchor="right",
                                      x=1,
                                     ))

    fig.update_yaxes(showline=True, linecolor='black', ticksuffix = "%", title='ISA base 2016-12', secondary_y=False)
    fig.update_yaxes(showline=True, linecolor='black', ticksuffix = "$", title='$ARS constantes', secondary_y=True)
    fig.update_xaxes(showline=True, linecolor='black')

    return fig

def plot_graduated_scattermap(points_gdf, polygons_gdf, indicator):
    '''
    Plots prices over time
    '''
    if 'COMUNA' in polygons_gdf.columns:
      hover_ref = 'barrio'
      z = 10
    else:
      hover_ref = 'localidad'
      z = 8

    lon = polygons_gdf.geometry.centroid.x.mean()
    lat = polygons_gdf.geometry.centroid.y.mean()
    coords = {"lat":lat, "lon":lon}
    districts = len(polygons_gdf)
    polygons_gdf['id'] = polygons_gdf.index

    X,Y = get_polygons_xy(polygons_gdf)

    points_gdf['y'] = points_gdf.geometry.y
    points_gdf['x'] = points_gdf.geometry.x
    fig = px.scatter_mapbox(points_gdf,
                            lat=points_gdf['y'],
                            lon=points_gdf['x'],
                            hover_name=hover_ref,
                            size=indicator,
                            animation_frame='periodo',
                            animation_group='localidad',
                            color_discrete_sequence=['#FFFF00'],
                            hover_data={'$ nominales':True, '$ constantes':True,
                                        'periodo':True, 'x':False,'y':False},
                            opacity=0.9,
                            height=600)

    fig2 = go.Figure(go.Scattermapbox(mode = "lines", fill = "toself",
                                      opacity=0,
                                      lon = X, lat = Y,
                                      hoverinfo='none'))

    fig.add_trace(fig2.data[0])

    fig.update_layout(mapbox={'style':"carto-darkmatter",
                              'center': {'lon': lon, 'lat': lat},
                              'zoom':z},
                      title_text = 'Evolucion de precios de alquiler por departamento: {}'.format(points_gdf.jurisdiccion.unique()[0]),
                      showlegend = False)
    fig.update_layout(margin={"r":1,"t":75,"l":0,"b":0},
                      mapbox=dict(
                                  pitch=0,
                                  bearing=0
                              ))

    return fig


def plot_density_scatter_map(points_df, polygons_gdf):
    if 'COMUNA' in polygons_gdf.columns:
      z = 10
    else:
      z = 8

    x = points_df.longitud.mean()
    y = points_df.latitud.mean()

    fig = px.density_mapbox(points_df,
                            lat="latitud",
                            lon="longitud", hover_name="region",
                            hover_data={'periodo':True, 'latitud':False,'longitud':False},
                            animation_frame="periodo",
                            opacity=0.7,
                            zoom=z, height=600)

    fig.update_layout(
        mapbox_layers=[{
                "source": json.loads(polygons_gdf.geometry.to_json()),
                "below": "traces",
                "type": "line",
                "color": "red",
                "line": {"width": 0.5},
            },
        ],
        mapbox_style="carto-darkmatter",
        mapbox = {'center': {'lon': x, 'lat': y - 0.025}},
        title_text = 'Oferta de departamento en alquiler: {}'.format(points_df.region.unique()[0])

    )


    fig.update_layout(margin={"r":1,"t":75,"l":0,"b":0},
                      mapbox=dict(
                                  pitch=0,
                                  bearing=0
                              ))
    return fig

def plot_folium_dual_choroplet(gdf_inferior, gdf_superior, categoria, indicador_superior, nombre_superior, nombre_region):
    centroide =  gdf_inferior.geometry.centroid
    coordenadas = [centroide.y.mean(), centroide.x.mean()]

    if nombre_region == 'Capital Federal':
        zoom_value = 11
    elif nombre_region == 'Bs.As. G.B.A. Zona Norte':
        zoom_value = 9
        coordenadas = [centroide.y.mean()+0.25, centroide.x.mean()]
    else:
        zoom_value = 10

    layer = folium.Map(location=coordenadas,
                       zoom_start=zoom_value,
                       height = 500,
                       control_scale=True,
                       tiles='cartodbpositron')

    tiles = ['openstreetmap', 'stamenterrain']
    for tile in tiles:
        folium.TileLayer(tile).add_to(layer)

    cut = mapclassify.NaturalBreaks(gdf_inferior[categoria],k=4)
    bins = [b for b in cut.bins]
    bins.insert(0, 0.00)

    area_inf = folium.Choropleth(name='Radios censales',
                                 geo_data=gdf_inferior,
                                 data=gdf_inferior[[c for c in gdf_inferior.columns if c!='geometry']],
                                 columns=['str_link', categoria],
                                 key_on='properties.str_link',
                                 fill_color='YlOrRd',
                                 bins = bins,
                                 fill_opacity=0.9,
                                 line_opacity=0.1,
                                 highlight=True,
                                 legend_name='Casos totales de la categoría {} a nivel inferior'.format(categoria),
                                 smooth_factor=1).add_to(layer)

    area_inf.geojson.add_child(folium.features.GeoJsonTooltip(fields=['str_link',categoria],
                                                              aliases=['Radio_id:',categoria.capitalize()+':']))

    cut = mapclassify.NaturalBreaks(gdf_superior[indicador_superior],k=4)
    bins = [b for b in cut.bins]
    bins.insert(0, 0.00)

    if nombre_region == 'Capital Federal':
        nombre_superior = nombre_superior.upper()
    else:
        pass

    area_sup = folium.Choropleth(name=nombre_superior.capitalize(),
                                 geo_data=gdf_superior,
                                 data=gdf_superior[[c for c in gdf_superior.columns if c!='geometry']],
                                 columns=[nombre_superior, indicador_superior],
                                 key_on='properties.'+nombre_superior,
                                 fill_color='Greys',
                                 bins = bins,
                                 fill_opacity=0.6,
                                 line_opacity=0.1,
                                 highlight=True,
                                 legend_name='Indice de concentración espacial para la categoría {}'.format(categoria),
                                 smooth_factor=1).add_to(layer)

    area_sup.geojson.add_child(folium.features.GeoJsonTooltip(fields=[nombre_superior, indicador_superior],
                                                              aliases=[nombre_superior+':', 'Concentración espacial:']))


    folium.LayerControl().add_to(layer)
    return layer
