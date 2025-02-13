# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requisitos y luego instálalos
COPY requirements_main.txt .
RUN pip install --no-cache-dir -r requirements_main.txt

# Copia todo el contenido del directorio actual en el contenedor
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5000

# Comando para correr la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]