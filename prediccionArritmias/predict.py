import pandas as pd  # type: ignore
import numpy as np
from sklearn.preprocessing import StandardScaler
from keras.saving import load_model  # type: ignore
from pathlib import Path  # type: ignore
from fastapi import FastAPI, Request, HTTPException, status  # type: ignore
from pydantic import BaseModel  # type: ignore
from jose import JWTError, jwt  # type: ignore

# from tensorflow.keras.layers import TSFMLayer
# data = pd.read_csv("Input_file.csv")
# import pipreqs

BASE_DIR = Path(__file__).resolve(strict=True).parent

__version__ = "1.0.0"
# models\1\LSTM--1.0.0.h5
model_path = "models/1/LSTM--1.0.0.h5"
model = load_model(model_path)
diccionario_clases = {
    0: "Arresto_cardiaco",
    1: "Bajo_gasto_cardiaco",
    2: "Sano",
    3: "Shock_cardiogenico",
}


app2 = FastAPI()


class BatchIn(BaseModel):
    idAtencion: int
    idSigno: dict
    nomSigno: dict
    valor: dict
    fecRegistro: dict

@app2.get("/")
async def read_root():
    return {"Home endpoint": "Model Prediction Service running..."}

@app2.post('/models')
async def predict(request: Request, payload: dict):

    try:
        # Accede a los headers de la petición
        print("Accediendo a los headers...")
        headers = request.headers
    except Exception as e:
        # print("Entrando a la excepcion")
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) + " " + "Error en el header"
        )

    if "token" not in headers:
        print("Opcion1")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )
    if headers.get('token') == "":
        print("Opcion2")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is empty"
        )
    if not isValidToken(headers.get('token')):
        print("Opcion3")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    df = pd.DataFrame.from_dict(payload)

    df_resultante = df.pivot_table(
        index=["idAtencion", "fecRegistro"], columns="nomSigno", values="valor"
    ).reset_index()

    # Mostrar el DataFrame resultante

    # filas_con_nan = df_resultante[df_resultante.isnull().all(axis=1)]

    # Se filtran los datos con mayor numero de datos no validos
    # para realizar el procesamiento
    columnas_deseadas = [
        "idAtencion",
        "fecRegistro",
        "MDC_BLD_PERF_INDEX",
        "MDC_ECG_HEART_RATE",
        "MDC_ECG_V_P_C_RATE",
        "MDC_LEN_BODY_ACTUAL",
        "MDC_MASS_BODY_ACTUAL",
        "MDC_PULS_OXIM_PULS_RATE",
        "MDC_PULS_OXIM_SAT_O2",
        "MDC_TEMP",
        "MDC_TTHOR_RESP_RATE",
    ]

    # Filtrar el DataFrame para incluir solo las columnas deseadas
    df_resultante_filtrado = df_resultante[columnas_deseadas]

    # Se usan los ultimos datos del paciente, es decir la ultima hora y
    # cuarenta minutos de datos registrados

    ultimas_20_filas_por_id = (
        df_resultante_filtrado
        .groupby("idAtencion")
        .tail(20)
    )

    df_resultante_lleno = ultimas_20_filas_por_id.ffill()

    # Caracteristicas seleccionadas

    selected_features = [
        "MDC_BLD_PERF_INDEX",
        "MDC_ECG_HEART_RATE",
        "MDC_ECG_V_P_C_RATE",
        "MDC_LEN_BODY_ACTUAL",
        "MDC_MASS_BODY_ACTUAL",
        "MDC_PULS_OXIM_PULS_RATE",
        "MDC_PULS_OXIM_SAT_O2",
        "MDC_TEMP",
        "MDC_TTHOR_RESP_RATE",
    ]

    features = df_resultante_lleno[selected_features]
    # Convertir los datos a secuencias por paciente
    sequences = []
    patient_ids = df_resultante_lleno["idAtencion"].unique()
    for patient_id in patient_ids:
        patient_data = features[
            df_resultante_lleno["idAtencion"] == patient_id
        ]
        sequences.append(patient_data.values)
    scaler = StandardScaler()
    X_test = [scaler.fit_transform(seq) for seq in sequences]
    X_test = np.reshape(X_test, (len(X_test), X_test[0].shape[0],
                                 X_test[0].shape[1]))

    # predicción del modelo
    results = pd.DataFrame()
    j = 0
    for i in range(len(X_test)):
        resultados = model.predict(X_test[i:])
        max_index = np.argmax(resultados)
        state = diccionario_clases[max_index]
        temp = pd.DataFrame(
            {"idAtencion": patient_ids[i], "Inference": [resultados],
             "State": state},
            index=[0],
        )
        results = pd.concat([results, temp])
        for idx, resultado in enumerate(resultados, start=1):
            j = j + 1
            # Obtener la clase con la probabilidad más alta
            # para este conjunto de resultados
            clase_predicha = np.argmax(resultado)

            # Obtener el nombre de la clase predicha
            nombre_clase_predicha = diccionario_clases[clase_predicha]

            # Mostrar el resultado
            print(
                f"Predicción {j}: El paciente con id {patient_ids[i]}\
                se encuentra en estado: {nombre_clase_predicha}"
            )
    # print(resultados.shape)
    # print(resultados)
    # result = await asyncio.sleep(0)

    inferences = results

    for item in inferences.columns:
        print(item)
    # print(json_inferences)
    np_inference = inferences.Inference.item()[0]
    inference = [float(x) for x in np_inference]
    print(type(inference))
    UserId = inferences.idAtencion.unique().item()
    UserId = int(UserId)
    # print(type(inferences))
    return {
        "idAtencion": UserId,
        "inferences": {
            "Arresto_Cardiaco": inference[0],
            "Bajo_Gasto_Cardiaco": inference[1],
            "Sano": inference[2],
            "Shock_Cardiogenico": inference[3],
        },
        "State": inferences.State.unique().item(),
    }


def isValidToken(token: str):

    secret_key = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcxODA2Mjk0NCwiaWF0IjoxNzE4MDYyOTQ0fQ.zN9eemsiMb7rGanbHVXumbU5wHJDnDBYg3jp8WoRaAg"

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(decoded_token is not None)
        return True
    except JWTError as e:
        print(e)
        return False
