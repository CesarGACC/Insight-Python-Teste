FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt
COPY ./lista_paises.json /code/lista_paises.json
COPY ./gerar_indicadores_aptos.csv /code/gerar_indicadores_aptos.csv

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]

RUN ls