# Use uma imagem leve oficial do Python
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /code

# Copia e instala dependências (camada de cache otimizada)
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia o código da aplicação
COPY ./app /code/app

# Expõe a porta
EXPOSE 8000

# Comando de execução
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]