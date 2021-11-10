### VISPREV UTILS ###

def devuelve_consulta(client, query):
    query_job = client.query(query)
    df = query_job.result().to_dataframe()
    return df
