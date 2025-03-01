import pandas as pd  # type: ignore
from pycaret.classification import load_model, predict_model  # type: ignore
from pathlib import Path  # type: ignore
from fastapi import FastAPI, Request, HTTPException, status  # type: ignore
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging  # type: ignore
from pydantic import BaseModel  # type: ignore
from jose import JWTError, jwt  # type: ignore
from dotenv import load_dotenv  # type: ignore
import os  # type: ignore

load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found in .env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve(strict=True).parent

__version__ = "1.0.0"
# models\1\saved_lr_model.plk
model_path = "models/1/saved_lr_model"
model = load_model(model_path)

diccionario_clases = {
    0: "Sano",
    1: "Fallo Cardiaco",
}


app2 = FastAPI()

# {"Age":40,"RestingBP":140,"Cholesterol":289,"FastingBS":0,"MaxHR":172,"Oldpeak":0.0,"Sex_M":true,"ChestPainType_ATA":true,"ChestPainType_NAP":false,"ChestPainType_TA":false,"RestingECG_Normal":true,"RestingECG_ST":false,"ExerciseAngina_Y":false,"ST_Slope_Flat":false,"ST_Slope_Up":true,"id":120273499993770023631873540801596256962}


class BatchIn(BaseModel):
    Age: int
    RestingBP: int
    Cholesterol: int
    FastingBS: int
    MaxHR: int
    Oldpeak: float
    Sex_M: bool
    ChestPainType_ATA: bool
    ChestPainType_NAP: bool
    ChestPainType_TA: bool
    RestingECG_Normal: bool
    RestingECG_ST: bool
    ExerciseAngina_Y: bool
    ST_Slope_Flat: bool
    ST_Slope_Up: bool
    id: int


@app2.get("/")
async def read_root():
    return {"Home endpoint": "Model Prediction Service running..."}


@app2.post("/models")
async def predict(request: Request, payload: BatchIn):

    try:
        # Accede a los headers de la petición
        print("Accediendo a los headers...")
        headers = request.headers
    except Exception as e:
        # print("Entrando a la excepcion")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e) + " " + "Error en el header",
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

    all_columns = [
        "Age",
        "RestingBP",
        "Cholesterol",
        "FastingBS",
        "MaxHR",
        "Oldpeak",
        "Sex_M",
        "ChestPainType_ATA",
        "ChestPainType_NAP",
        "ChestPainType_TA",
        "RestingECG_Normal",
        "RestingECG_ST",
        "ExerciseAngina_Y",
        "ST_Slope_Flat",
        "ST_Slope_Up",
        "id",
    ]
    # Convertir payload a DataFrame correctamente
    df_resultante = pd.DataFrame([payload.model_dump()])  # O usa payload.dict() si es Pydantic v1

    # Asegurar que contiene las columnas necesarias
    df_resultante = df_resultante[all_columns]

    columnas_deseadas = [
        "Age",
        "RestingBP",
        "Cholesterol",
        "FastingBS",
        "MaxHR",
        "Oldpeak",
        "Sex_M",
        "ChestPainType_ATA",
        "ChestPainType_NAP",
        "ChestPainType_TA",
        "RestingECG_Normal",
        "RestingECG_ST",
        "ExerciseAngina_Y",
        "ST_Slope_Flat",
        "ST_Slope_Up",
    ]

    logger.debug("------------------DF obtained----------------------")
    logger.debug(f"Columns in df_resultante: {df_resultante.columns}")

    # Filtrar el DataFrame para incluir solo las columnas deseadas
    df_resultante_filtrado = df_resultante[columnas_deseadas]

    features = df_resultante_filtrado.copy()
    # Convertir los datos a secuencias por paciente
    patient_id = df_resultante["id"].unique()

    # Prediction
    results = predict_model(model, data=features)
    label_pred = results.iloc[0]["prediction_label"]
    score_pred = results.iloc[0]["prediction_score"]
    state = diccionario_clases[label_pred]
    temp = pd.DataFrame(
        {"idAtention": patient_id, "Score": score_pred, "State": state},
        index=[0],
    )
    # results = pd.concat([results, temp])
    print(
        f"Predicción: El paciente con id {patient_id}\
            se encuentra en estado: {state}"
    )

    inference = temp
    if label_pred == 0:
        inference["Sano_prob"] = score_pred
        inference["Ataque Cardiaco_prob"] = 1 - score_pred
    elif label_pred == 1:
        inference["Sano_prob"] = 1 - score_pred
        inference["Ataque Cardiaco_prob"] = score_pred

    return {
        "idPatient": inference.iloc[0]["idAtention"],
        "inferences": {
            "Sano": inference.iloc[0]["Sano_prob"],
            "Ataque Cardiaco": inference.iloc[0]["Ataque Cardiaco_prob"],
        },
        "State": inference.iloc[0]["State"],
    }


def isValidToken(token: str):

    secret_key = API_KEY

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(decoded_token is not None)
        return True
    except JWTError as e:
        print(e)
        return False


@app2.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )