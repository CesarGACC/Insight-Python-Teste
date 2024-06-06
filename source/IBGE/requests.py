import requests
#from IBGE import postgresdb

def pesquisas():
    response = requests.get("https://servicodados.ibge.gov.br/api/v1/pesquisas") 
    return response.json()