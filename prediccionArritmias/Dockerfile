# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /predicionArritmias

# Copia el archivo de requisitos y luego instálalos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del directorio actual en el contenedor
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 5001

# Establece la variable de entorno con valor por defecto
# ENV UVICORN_WORKERS=4

# Comando para correr la aplicación usando la variable de entorno
# CMD ["uvicorn", "predict:app2", "--host", "0.0.0.0", "--port", "5001", "--workers", "${UVICORN_WORKERS}"]

# Comando para correr la aplicación
CMD ["uvicorn", "predict:app2", "--host", "0.0.0.0", "--port", "5001"]