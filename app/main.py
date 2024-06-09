from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder

from app.IBGE import ibge as ibge_requests

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello!"

@app.get("/ibge/paises/")
async def ibge_pais():
    return Response(content=ibge_requests.lista_paises(), media_type='application/json')

@app.get("/ibge/indicadores/")
async def ibge_pais():
    return Response(content=ibge_requests.lista_indicadores(), media_type='application/json')

@app.get("/ibge/pais/{pais_string}")
async def ibge_apto_pais(pais_string: str):
    return Response(content=ibge_requests.apto_pais(pais_string), media_type='application/json')

@app.get("/ibge/pais/{pais_string}/indicadores/{indicador_tipo}")
async def ibge_apto_pais_indicadores(pais_string: str, indicador_tipo:str):
    return Response(content=ibge_requests.apto_pais_indicadores("",pais_string,indicador_tipo), media_type='application/json')

@app.get("/ibge/bloco/{bloco_string}/pais/{pais_string}")
async def ibge_apto_bloco_pais(bloco_string:str, pais_string: str):
    return Response(content=ibge_requests.apto_pais_indicadores(bloco_string, pais_string, ""), media_type='application/json')

@app.get("/ibge/bloco/{bloco_string}/pais/{pais_string}/indicadores/{indicador_tipo}")
async def ibge_bloco_pais_indicadores_apto(bloco_string:str, pais_string: str, indicador_tipo:str):
    return Response(content=ibge_requests.apto_pais_indicadores(bloco_string,pais_string, indicador_tipo), media_type='application/json')

@app.get("/ibge/apto/")
async def ibge_bloco_pais_indicadores_apto(bloco_string: str = "BR|CN", pais_string: str = "AR", indicador_tipo: str = "Economia"):
    return Response(content=ibge_requests.apto_pais_indicadores(bloco_string,pais_string, indicador_tipo), media_type='application/json')
