##########################################
# VISPREV - Visor de precios de vivienda #
##########################################
from google.cloud import bigquery
from google.oauth2 import service_account

import streamlit as st
import os
from utils import *
from datasources import *
import yaml
import pandas as pd
from datetime import datetime

def query_properati_data(first_year,last_year,first_month,last_month):
    '''
    Query the properati-data-public datasource on Google bigquery
    to get nominal series of rents values in the Buenos Aires
    Metropolitan Area.

    Parameters
    ----------
    first_year (str): starting year for period filtering
    last_year (str): ending year for period filtering
    first_month (str): starting month for period filtering
    last_month (str): ending period month for period filtering
    ...
    Returns
    pd.DataFrame: long df with period/region/value fields
    '''
    # price series for maps
    QUERY0 = """SELECT place.l2 as jurisdiccion,
                       place.l3 as localidad,
                       FORMAT_DATE('%m-%Y', start_date) as periodo,
                       AVG(property.price) AS monto
                FROM `properati-dw.public.ads`
                WHERE start_date >= "2015-01-01" AND end_date <= "2021-12-31"
                AND property.operation = "Alquiler"
                AND property.currency = "ARS"
                AND place.l2 IN ('Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte', 'Capital Federal', 'Bs.As. G.B.A. Zona Sur')
                AND property.type = "Departamento"
                GROUP BY
                jurisdiccion,
                place.l3,
                periodo
                ORDER BY
                periodo DESC"""

    # llamar cada tabla del conjunto de datos
    QUERYI =  """SELECT state_name as jurisdiccion,
                        FORMAT_DATE('%m-%Y', start_date) as periodo,
                        AVG(price) AS monto
                 FROM `properati-data-public.properties_ar.properties_rent_{}*`
                 WHERE _TABLE_SUFFIX >= '{}' AND _TABLE_SUFFIX <= '{}'
                 AND state_name IN ('Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte',
                                    'Capital Federal', 'Bs.As. G.B.A. Zona Sur')
                 AND currency LIKE 'ARS'
                 AND property_type LIKE 'apartment'
                 GROUP BY
                     jurisdiccion,
                     periodo
                 ORDER BY
                   periodo DESC""".format(year, first_month, last_month)

    # lat/lon for density
    QUERYIII = """SELECT place.lat as latitud,
                         place.lon as longitud,
                         place.l3 as localidad,
                         FORMAT_DATE('%m-%Y', start_date) as periodo,
                  FROM `properati-dw.public.ads`
                  WHERE start_date >= "2015-01-01" AND end_date <= "2021-12-31"
                  AND property.operation = "Alquiler"
                  AND property.currency = "ARS"
                  AND place.l2 IN ('Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte', 'Capital Federal', 'Bs.As. G.B.A. Zona Sur')
                  AND property.type = "Departamento"
                  ORDER BY
                  periodo DESC"""

    start_period = first_year + '-' + first_month + '-01'
    end_period = last_year + '-' + last_month + '-01'

    QUERYII = """SELECT place.l2 as jurisdiccion,
                        FORMAT_DATE('%m-%Y', start_date) as periodo,
                        AVG(property.price) AS monto
                 FROM `properati-dw.public.ads`
                 WHERE start_date >= "{}" AND end_date <= "{}"
                 AND property.operation = "Alquiler"
                 AND property.currency = "ARS"
                 AND place.l2 IN ('Bs.As. G.B.A. Zona Oeste', 'Bs.As. G.B.A. Zona Norte',
                                  'Capital Federal', 'Bs.As. G.B.A. Zona Sur')
                 AND property.type = "Departamento"
                 GROUP BY
                 jurisdiccion,
                 periodo
                 ORDER BY
                 periodo DESC""".format(start_period, end_period)

    with open(os.getenv('config', ".") + "/config/ssyt_settings.yaml") as f:
        cfg = yaml.safe_load(f)

    project_id = cfg['bigquery']['project_id']
    service_account_key = cfg['bigquery']['credentials']

    key = service_account.Credentials.from_service_account_file(service_account_key)
    client = bigquery.Client(credentials=key,project=project_id)

    # Should work with QUERY I and II. Doesn't chhose I because it only returns values up to 2018
    df = devuelve_consulta(client=client, query=QUERYII)

    return df

def get_properati_data(first_year,last_year, first_month,last_month):
    '''
    '''
    df = get_nominal_prices_from_2015_to_2021()
    start_date = first_year + '-' + first_month
    end_date = last_year + '-' + last_month
    df['periodo_date'] = pd.to_datetime(df['periodo'], format='%m-%Y')
    df_f = df.loc[(df['periodo_date']>=start_date) & ((df['periodo_date']<=end_date))].copy()
    df_f.drop(columns='periodo_date', inplace=True)
    return df_f


def choose_jurisdiction(df, region):
    '''
    Recibe una serie de precios globales o por jurisdiccion y la deflacta en base
    a un periodo base.
    '''
    rents_gba_region = df.pivot(index='periodo', columns='jurisdiccion', values='monto')

    dt_index = pd.to_datetime(
                               dict(
                                     year=rents_gba_region.index.str[3:],
                                     month=rents_gba_region.index.str[:2],
                                     day=1
                                    )
                            )
    sorted_periods = dt_index.sort_values(ascending=True).astype('str')
    reordered_periods = sorted_periods.apply(lambda x: str(x)[5:7]+'-'+str(x)[:4])

    unique_periods = [i for i in reordered_periods]
    gba_regions = rents_gba_region.reindex(unique_periods)
    gba_regions.reset_index(inplace=True)
    gba_region = gba_regions[['periodo',region]].copy()

    gba_region.columns = ['period', 'price']

    months = gba_region['period'].apply(lambda x: x.split('-')[0])
    years = gba_region['period'].apply(lambda x: x.split('-')[1])
    clean_months = []
    for m in months:
        if m[0]=='0':
            clean_months.append(m[1])
        else:
            clean_months.append(m)

    months = pd.Series(clean_months)
    u_score = ['-'] * len(months)
    u_scores = pd.Series(u_score)
    period_form = years + u_scores + months
    gba_region['period'] = period_form

    return gba_region

def formatea_isa(isa, serie='indice_salarios'):
    '''
    Formatea dataframe con indice de precios
    ...
    isa(df): indice de salarios - ver formato en dataframe
    serie(str): default con el nombre de la serie a utilizar

    Devuelve:
    pandas.Series: serie con indice de salarios emparejado al año base del IPC
    '''

    # hacemos slicing sobre los strings de fecha para quedarnos con el periodo
    isa['periodo'] = isa.indice_tiempo.apply(lambda x: x[:7])
    # filtramos desde el periodo de referencia (octubre de 2016)
    isa_f = isa.set_index('periodo').loc['2016-10':].copy()
    # como nuestro ipc esta en base dicimiebre 2016, vamos a llevar el isa al mismo periodo
    isa_f.drop(columns='indice_tiempo', inplace=True)

    # filtramos nuestro isa en base al periodo disponible del ipc,
    # esto se podría parametrizar en función de esa disponibilidad. Pero dejemoslo así, simple.
    isa_rebase = isa_f.apply(lambda x: x/isa_f.loc['2016-12'], axis=1)
    # renombramos los periodos para ajustar el formato que traemos de antes
    isa_rebase.index = isa_rebase.index.str.replace('-0', '-', regex=False)
    # nuestro ipc va de enero 2017 en adelante, hacemos slicing desde ahi
    isa_rebase = isa_rebase.loc['2017-1':].copy()
    return isa_rebase[serie]

def read_icl():
    icl_bcra = get_icl_bcra()
    icl_bcra['Mes'] = icl_bcra.Fecha.apply(lambda x: x.split('/')[2] + '-' + x.split('/')[1])
    # reemplazamos las comas y convertimos nuestro valores en float
    icl_bcra['Valor'] = icl_bcra['Valor'].str.replace(',', '.', regex=False)
    icl_bcra['Valor'] = icl_bcra.Valor.apply(lambda x: float(x))
    icl_bcra = icl_bcra.drop_duplicates(subset='Mes', keep='last')
    icl_bcra = icl_bcra[['Valor','Mes']].set_index('Mes')
    # renombramos nuestro indice, para que matchee con nuestra serie de valores
    icl_bcra.index = icl_bcra.index.str.replace('-0', '-', regex=False)
    return icl_bcra['Valor']

def aperturas_ipc_indec(df, rubro):
    aperturas = df.set_index('Región GBA')
    apertura_elegida = aperturas.loc[rubro]
    return apertura_elegida

def read_ipc():
    ipc_crudo = get_ipc_indec()

    # hacemos slicing desde las filas 5 a la 53, el IPC para GBA
    ipc_crudo = ipc_crudo.iloc[5:53].copy()
    # renombramos columnas
    ipc_crudo.columns = ipc_crudo.iloc[0]
    ipc_indec = ipc_crudo.iloc[3:].copy()

    # armo de nuevo el nombre de las columnas
    new_columns = []
    for i in ipc_indec.columns:
      if i != 'Región GBA':
        y = i.year # el item que estamos iterando ya es un datetime!
        m = i.month
        fecha = '{}-{}'.format(y,m)
        new_columns.append(fecha)
      else:
        new_columns.append(i)

    ipc_indec.columns = new_columns
    ipc_indec.reset_index(inplace=True)
    ipc_indec.drop(columns='index', inplace=True)

    return ipc_indec

def deflactar_serie(pe,pr,ba, # en primer lugar, fijense que renombramos varios parametros
                    construye_d,
                    ipc,
                    isa,
                    rubro_ipc='Nivel general',
                    rubro_isa='indice_salarios',
                    d=None):
    '''
    Deflacta una serie de valores nominales
    ...
    pe(str): nombre de la serie con la etiqueta del periodo nominal
    pr(str): nombre de la serie con valores nominales
    ba(str): nombre del periodo que vamos a tomar como base
    construye_d(bool): construir el deflactor en el cuerpo de la funcion (e.g:False)
                       Nota alumnos: este parametro es default, si no lo especifican
                         a la hora de ejecutar la funcion se va a tomar True como valor.
    ipc(serie): serie de pandas con variaciones porcentuales de precios
    isa(serie): serie de pandas con variaciones porcentuales de salarios
    rubro_ipc(str): nombre de la apertura del ipc. El default es 'Nivel general', pero
                    también se puede cambiar cuando se ejecuta la función.
    rubro_isa(str): nombre del tipo de indice salarial de referencia. El default también
                    se puede cambiar por otro nombre.
    d(str): serie de pandas con un índice deflactor.
    Devuelve:
    pd.Series: Serie de tuplas.
    '''
    periodo = pe
    precio_nominal = pr
    periodo_base = ba

    if construye_d: # si esto evalua a True
        precios = aperturas_ipc_indec(ipc, rubro_ipc)
        salarios = formatea_isa(isa, rubro_isa)
        serie = salarios/precios.mean() # entonces construimos nuestro deflactor,
                                        # en nuestro caso expresamos las variaciones mensuales
                                        # de los salarios en función del promedio de las
                                        # variaciones de precios

    else:
        serie = d # sino, usamos uno ya armado (como el ICL)

    # en esta seccion deflactamos
    serie_periodo = serie.loc[periodo]
    serie_base = serie.loc[periodo_base]
    coeficiente = serie_periodo/serie_base
    precio_constante = precio_nominal / coeficiente

    return periodo, precio_nominal, coeficiente, serie_base, serie_periodo, precio_constante
