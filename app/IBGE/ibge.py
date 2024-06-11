import requests
import pandas as pd
import json
import os
from typing import Dict
#from IBGE import postgresdb


def apto_pais(pais:str):
    if(not validation_pais(pais)): return False
    if(not validation_bloco("BR|RU|IN|CN|ZA")): return False

    gerar_indicadores()
    list_indicadores = ["Economia","Indicadores sociais","Meio Ambiente","População","Redes","Saúde"]
    string_indicadores = get_string_indicadores(list_indicadores)
    
    string_bloco = gerar_bloco("BR|RU|IN|CN|ZA",string_indicadores)

    df_bloco = get_bloco()
    df_bloco_intermiatiate = get_intermitiate_dataframe(df_bloco)
    df_bloco_sorted = get_sorted(df_bloco_intermiatiate)

    gerar_pais(pais, string_indicadores)
    df_pais = get_pais(pais)
    df_pais_intermiatiate = get_intermitiate_dataframe(df_pais)
    df_pais_sorted = get_sorted(df_pais_intermiatiate)

    return pais_e_apto(df_bloco_sorted,df_pais_sorted, pais, string_bloco)

def apto_pais_indicadores(bloco:str, pais:str, indicador_tipo:str):
    if(not validation_pais(pais)): return False
    if(not validation_bloco(bloco)): return False

    if(bloco==""): 
        bloco = "BR|RU|IN|CN|ZA" #default brics

    gerar_indicadores()
    list_indicadores = string_to_list(indicador_tipo)
    string_indicadores = get_string_indicadores(list_indicadores)
    print(string_indicadores)
    string_bloco = gerar_bloco(bloco, string_indicadores)

    df_bloco = get_bloco()
    df_bloco_intermiatiate = get_intermitiate_dataframe(df_bloco)
    df_bloco_sorted = get_sorted(df_bloco_intermiatiate)

    gerar_pais(pais, string_indicadores)
    df_pais = get_pais(pais)
    df_pais_intermiatiate = get_intermitiate_dataframe(df_pais)
    df_pais_sorted = get_sorted(df_pais_intermiatiate)

    return pais_e_apto(df_bloco_sorted,df_pais_sorted, pais, string_bloco)

def validation_pais(pais:str):
    if(len(pais)!=2): return False

    result = []
    lista_paises = json.load(open("lista_paises.json","r",encoding="utf8"))
    for key in lista_paises:
        if(key.get(pais)!=None):
            result.append(key.get(pais))

    if(len(result)==0):
        return False

    return True

def validation_bloco(bloco:str):
    if(bloco==""):
        return True

    lista_bloco = string_to_list(bloco)

    found = False
    for item in lista_bloco:
        if(validation_pais(item)):
            found = True
    return found

def string_to_list(string:str):
    lista = string.split("|")
    return lista

def gerar_pais(pais:str,string_indicadores:str):
    """     if(os.path.exists(f"{pais}_apto_pais.json")):
        return """
    response = requests.get(f"https://servicodados.ibge.gov.br/api/v1/paises/{pais}/indicadores/{string_indicadores}") 
    json.dump(response.json(), open(f"{pais}_apto_pais.json", "w", encoding="utf8"), indent=4, ensure_ascii=False)

def get_pais(pais:str):
    return pd.DataFrame.from_dict(json.load(open(f"{pais}_apto_pais.json","r",encoding="utf8")))

def gerar_bloco(string_bloco:str,string_indicadores:str):
    """     if(os.path.exists("apto_paises_bloco.json")):
        return """

    response = requests.get(f"https://servicodados.ibge.gov.br/api/v1/paises/{string_bloco}/indicadores/{string_indicadores}") 
    json.dump(response.json(), open("apto_paises_bloco.json", "w", encoding="utf8"), indent=4, ensure_ascii=False)

    return string_bloco

def get_bloco() -> pd.DataFrame:
    return pd.DataFrame.from_dict(json.load(open("apto_paises_bloco.json","r",encoding="utf8")))

def gerar_indicadores():
    """     if(os.path.exists("indicadores.json")):
        return """
    response = requests.get(f"https://servicodados.ibge.gov.br/api/v1/paises/indicadores/") 
    json.dump(response.json(), open("indicadores.json", "w", encoding="utf8"), indent=4, ensure_ascii=False)

def get_indicadores() -> pd.DataFrame:
    dt_indicadores = pd.DataFrame.from_dict(json.load(open("indicadores.json","r",encoding="utf8")))
    indicador_rows = []
    for _, line in dt_indicadores.iterrows():
        id = line['id']
        unidade = line['unidade']['id'] if isinstance(line['unidade'], Dict) else None
        indicador_split = line['indicador'].split(' - ')
        indicador_rows.append((id, indicador_split[0], indicador_split[1], unidade))

    return pd.DataFrame(indicador_rows, columns=['id', 'tipo', 'indicador', 'unidade'])

def get_unidade_por_indicador(indicador:str):
    indicadores = get_indicadores()
    return indicadores.query(f"indicador==\'{indicador.split(' - ')[1]}\'")["unidade"].values[0]

def get_valor_por_indicador(df:pd.DataFrame, indicador:str):
    return df.query(f"indicador==\'{indicador}\'")["valor"].values[0]

    
def get_intermitiate_dataframe(dt_base:pd.DataFrame)-> pd.DataFrame:

    result = []
    dt_base = dt_base.explode("series")
    dt_base["unidade"] = [item["id"] if isinstance(item, Dict) else None for item in dt_base["unidade"]]
    dt_base["pais"] = [item["pais"]["nome"] if isinstance(item, Dict) else None for item in dt_base["series"]]
    for _,row in dt_base.iterrows():
        for dict in row["series"]["serie"]:
            for k,v in dict.items():
                result.append([row["pais"],row["indicador"],k,v,row["unidade"]])

    dt_result = pd.DataFrame(result,columns=["pais","indicador","ano","valor","unidade"])
    dt_result = dt_result.dropna(subset=["valor"])
    dt_result["valor"] = dt_result["valor"].apply(float)
    dt_result = dt_result.sort_values(["pais","indicador","ano"], ascending=False)
    return dt_result

def get_sorted(dt_base:pd.DataFrame):
    unique_pais = dt_base["pais"].unique()
    unique_indicador = dt_base["indicador"].unique()

    #Media dos ultimos 5 resultados por pais/indicador
    media_result = []
    for pais in unique_pais:
        for indicador in unique_indicador:
            mean = dt_base[(dt_base["pais"] == pais) & (dt_base["indicador"] == indicador)].dropna(subset=["valor"]).head(5).loc[:, "valor"].mean(skipna=True).round(2)
            unidade = get_unidade_por_indicador(indicador)
            media_result.append([pais,indicador,mean,unidade])

    dt_media = pd.DataFrame(media_result, columns=["pais","indicador","media","unidade"])

    #Minimo das medias por indicador
    min_result=[]
    for indicador in unique_indicador:
        min = dt_media[(dt_media["indicador"] == indicador)].dropna(subset=["media"]).loc[:, "media"].min()
        min_result.append([indicador,min,get_unidade_por_indicador(indicador)])

    dt_min_result = pd.DataFrame(min_result, columns=["indicador","valor","unidade"])

    return dt_min_result
    
def get_string_indicadores(list_indicadores):
    df_indicadores = get_indicadores()

    string_indicadores = ""
    for _, row in df_indicadores.iterrows():
        for indicador in list_indicadores:
            if(indicador == row["tipo"]):
                string_indicadores = string_indicadores + "|" + str(row["id"])
    string_indicadores = string_indicadores[1:]

    if(len(string_indicadores)==0): 
        string_indicadores = get_string_indicadores(["Economia","Indicadores sociais","Meio Ambiente","População","Redes","Saúde"])

    return string_indicadores

def pais_e_apto(df_bloco:pd.DataFrame, df_pais:pd.DataFrame, pais:str, string_bloco:str):
    unique_indicadores = df_bloco["indicador"].unique()
    result = []

    indicadores_apto = pd.read_csv("gerar_indicadores_aptos.csv")
    for indicador in unique_indicadores:
        brics_value = get_valor_por_indicador(df_bloco,indicador) 
        pais_value = get_valor_por_indicador(df_pais,indicador) 
        unidade = get_unidade_por_indicador(indicador)
        
        i_apto = indicadores_apto.query(f"indicador==\'{indicador.split(' - ')[1]}\'")["apto"].values[0]

        if(i_apto == "neutro"):
            apto = True
        elif(i_apto == "maior"):
            if(brics_value <= pais_value):
                apto = True
            else:
                apto = False
        elif(i_apto == "menor"):
            if(brics_value >= pais_value):
                apto = True
            else:
                apto = False

            
        result.append([indicador, brics_value, pais_value, unidade, apto])

    dt_result = pd.DataFrame(result, columns=["indicador", "referencia", "valor", "unidade", "apto"])

    
    #gerar bloco
    lista_bloco = string_to_list(string_bloco)
    
    lista_paises = json.load(open("lista_paises.json","r",encoding="utf8"))
    bloco_result = []
    for item in lista_bloco:
        for key in lista_paises:
            if(key.get(item)!=None):
                bloco_result.append(key.get(item))
    
    pais_result = ""
    for key in lista_paises:
        if(key.get(pais)!=None):
            pais_result = ""+key.get(pais)

    result_json = dt_result.to_json(orient="table")
    parsed = json.loads(result_json)
    parsed.update({"bloco":bloco_result})
    parsed.update({"pais":pais_result})
    parsed.pop("schema")
    return json.dumps(parsed, indent=4, ensure_ascii=False)

def lista_paises():
    return json.dumps(json.load(open("lista_paises.json","r",encoding="utf8")), indent=4, ensure_ascii=False)

def lista_indicadores():
    gerar_indicadores()
    parsed = json.loads(get_indicadores().to_json(orient="table"))
    parsed.pop("schema")
    return json.dumps(parsed, indent=4, ensure_ascii=False)
