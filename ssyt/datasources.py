import streamlit as st
import geopandas as gpd
import pandas as pd


@st.cache(allow_output_mutation=True)
def get_nominal_prices_from_2015_to_2021():
    df = pd.read_csv('data/precios_nominales_2015-21.csv')
    return df

@st.cache(allow_output_mutation=True)
def get_icl_bcra():
    '''
    Indice de Contratos de Locacion - BCRA
    '''
    df = pd.read_excel('data/indice_contratos_locacion_nov2021.xls')
    return df

@st.cache(allow_output_mutation=True)
def get_ipc_indec():
    '''
    Indice de precios al consumidor - INDEC
    '''
    df = pd.read_excel('data/sh_ipc_aperturas.xls', sheet_name='Variación mensual aperturas', header=None)
    return df

@st.cache(allow_output_mutation=True)
def get_wages():
    '''
    Indice de salarios - Subsecretaria de Programacion Economica
    https://datos.gob.ar/dataset/sspm-indice-salarios-base-octubre-2016/archivo/sspm_149.1
    '''
    df = pd.read_csv('data/indice-salarios-mensual-base-octubre-2016_2021.csv')
    return df

@st.cache(allow_output_mutation=True)
def nominal_prices_over_time_caba():
    gdf = gpd.read_file('data/caba_nominales_012015_072021.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def nominal_prices_over_time_gba_oeste():
    gdf = gpd.read_file('data/zoeste_012015_072021.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def nominal_prices_over_time_gba_norte():
    gdf = gpd.read_file('data/znorte_nominales_012015_072021.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def nominal_prices_over_time_gba_sur():
    gdf = gpd.read_file('data/zsur_nominales_012015_072021.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def caba_neighborhood_limits():
    gdf = gpd.read_file('data/caba_barrios.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def gba_oeste_dept_limits():
    gdf = gpd.read_file('data/zoeste_deptos.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def gba_norte_dept_limits():
    gdf = gpd.read_file('data/znorte_deptos.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def gba_sur_dept_limits():
    gdf = gpd.read_file('data/zsur_deptos.zip')
    return gdf

@st.cache(allow_output_mutation=True)
def caba_rents_offer():
    df = pd.read_csv('data/caba_rents_offer.csv')
    return df

@st.cache(allow_output_mutation=True)
def gba_oeste_rents_offer():
    df = pd.read_csv('data/gbaoeste_rents_offer.csv')
    return df

@st.cache(allow_output_mutation=True)
def gba_norte_rents_offer():
    df = pd.read_csv('data/gbanorte_rents_offer.csv')
    return df

@st.cache(allow_output_mutation=True)
def gba_sur_rents_offer():
    df = pd.read_csv('data/gbasur_rents_offer.csv')
    return df

@st.cache(allow_output_mutation=True)
def adjust_prices_by_inflation_table(df, index_name,base):
    df_ = df.rename(columns={'indice_per':'{}'.format(index_name.lower()),
                             'indice_base': '{}'.format(index_name.lower())+' base'+'('+base+')',
                             'precio_nom':'$ARS nominales',
                             'precio_con':'$ARS constantes',
                             'coeficiente': 'Coeficiente de ajuste',
                             'region':'Region',
                             'periodo':'Periodo'})

    df_['$ARS constantes (%)'] = round(df_['$ARS constantes'].pct_change() * 100, 2)
    df_['{}'.format(index_name)+'(%)'] = round(df_['{}'.format(index_name.lower())].pct_change() * 100, 2)

    columns = ['Periodo', '$ARS nominales',
               '{}'.format(index_name.lower()),
               '{}'.format(index_name.lower())+' base'+'('+base+')',
               'Coeficiente de ajuste',
               '$ARS constantes',
               '{}'.format(index_name)+'(%)',
               '$ARS constantes (%)'
               ]

    df__ = df_[columns]

    return df__
