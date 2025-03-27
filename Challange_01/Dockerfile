# Usa uma imagem base leve com Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copia os arquivos da aplicação para o container
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Cria o diretório para armazenar reviews (evita erro de diretório inexistente)
RUN mkdir -p /app/reviews

# Expõe a porta 8082
EXPOSE 8082

# Executa a aplicação usando Gunicorn (melhor para Docker)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8082", "app.app:app"]
