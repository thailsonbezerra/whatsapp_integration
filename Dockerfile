# etapa de build (opcional aqui, mas prepara o ambiente)
FROM python:3.11-slim AS base

# configura diretório de trabalho
WORKDIR /app

# evita buffering para logs
ENV PYTHONUNBUFFERED=1

# instalar dependências do sistema necessárias (ajuste se precisar de mais)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# copiar requirements (você pode gerar antes)
COPY requirements.txt .

# instalar dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copiar o código da aplicação
COPY . .

# expor porta
EXPOSE 8000

# comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
