import pandas as pd
import requests
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException


class BatchIn(BaseModel):
    idAtencion: int
    idSigno: dict
    nomSigno: dict
    valor: dict
    fecRegistro: dict


class PredictionOut(BaseModel):
    idAtencion: int
    inferences: dict
    State: str


app = FastAPI()


@app.post("/predict")
async def generate_inference(
    payload: BatchIn,
    status_code=status.HTTP_200_OK,
):
    # Crear DataFrame para enviar a la función predict
    # data = #pd.DataFrame(
    data = {
            "idAtencion": payload.idAtencion,
            "nomSigno": payload.nomSigno,
            "valor": payload.valor,
            "fecRegistro": payload.fecRegistro,
            }
    # ).to_dict(orient="records")

    # inferences = await predict(data)
    port_HTTP = '5000'
    # ip = "127.0.0.1"
    ip = "localhost"
    uri = ''.join(['http://', ip, ':', port_HTTP, '/models'])
    # print(data)
    try:
        inferences = requests.post(uri, json=data)
        inferences.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
    # Ensure the response is JSON serializable
    try:
        response_json = inferences.json()
    except ValueError as e:
        return {"error": "Invalid JSON response from model endpoint"}

    return response_json
    """print(inferences)
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
    }"""
    # return inferences
