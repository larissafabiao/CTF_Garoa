# Usa uma imagem base leve com Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY . .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
# COPY . .

# Create the `reviews` directory, set permissions, and ensure it is owned by the default user
RUN mkdir -p reviews && chmod 777 reviews

# Add the hidden flag in the system file /etc/flag
RUN echo "HIK_VILLAGEAI_30e47959bc2877aa204b1bdf12170916" > /etc/flag

# Cria o diretório para armazenar reviews (evita erro de diretório inexistente)
RUN mkdir -p /app/reviews

# Expõe a porta 8082
EXPOSE 8082

# Executa a aplicação usando Gunicorn (melhor para Docker)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8082", "app.app:app"]
