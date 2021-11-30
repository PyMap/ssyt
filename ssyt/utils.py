import json
import pandas as pd
### VISPREV UTILS ###

def devuelve_consulta(client, query):
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df

def filter_data_on_period(df, first_year, first_month, last_year, last_month):
    start_date = first_year + '-' + first_month
    end_date = last_year + '-' + last_month
    df['periodo_date'] = pd.to_datetime(df['periodo'], format='%m-%Y')
    df_f = df.loc[(df['periodo_date']>=start_date) & ((df['periodo_date']<=end_date))].copy()
    df_f.drop(columns='periodo_date', inplace=True)
    return df_f

def get_polygons_xy(polygons_gdf):
    from_json = polygons_gdf.to_json()
    geoJSON = json.loads(from_json)

    pts=[]
    for  feature in geoJSON['features']:
        if feature['geometry']['type']=='Polygon':
            pts.extend(feature['geometry']['coordinates'][0])
            pts.append([None, None])

        elif feature['geometry']['type']=='MultiPolygon':
            for polyg in feature['geometry']['coordinates']:
                pts.extend(polyg[0])
                pts.append([None, None])#end of polygon
        else: raise ValueError("geometry type irrelevant for map")

    X, Y=zip(*pts)

    return X, Y
