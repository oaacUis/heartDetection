from fastapi import FastAPI, status, Depends, HTTPException, Request  # type: ignore
from pydantic import BaseModel  # type: ignore
import requests
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware  # type: ignore
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session  # type: ignore
from routes import auth
from routes.auth import get_current_user
from utils.logger import logger
from utils.middleware import middleware_log
from utils import models
from jose import JWTError, jwt 
from routes.auth import Token, ALGORITHM, SECRET_KEY


app = FastAPI()
app.include_router(auth.router)
models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


app.add_middleware(BaseHTTPMiddleware, dispatch=middleware_log)

logger.info("Starting API...")


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


@app.get("/", status_code=status.HTTP_200_OK)
async def user(payload: dict):
    """
    Retrieve user information.

    Parameters:
    - user: The user object containing user information.
    - db: The database dependency.

    Returns:
    - A dictionary containing the user information.

    Raises:
    - HTTPException with status code 401 if authentication fails.
    """
    if isValidToken(payload.get('token')) is False:
        raise HTTPException(status_code=401, detail="Token is not valid.")
    else:
        payload = jwt.decode(payload.get('token'),SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
    return {"User": username}


@app.get("/home")
async def home():
    """
    Endpoint for the home page.

    Returns:
        dict: A dict containing the health check status and model version.
    """
    await asyncio.sleep(0)  # type: ignore
    API_version = "1.0.0"
    return {"health_check": "OK", "API_version": API_version}


def isValidToken(token: str):

    secret_key = SECRET_KEY

    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        print(decoded_token is not None)
        return True
    except JWTError as e:
        print(e)
        return False


@app.post("/predict")  # , response_model=PredictionOut)
async def generate_inference(payload: BatchIn, request: Request):
    headers = request.headers
    if isValidToken(headers.get('token')) is False:
        raise HTTPException(status_code=401, detail="Invalid_Token")
    else:
        data = {
            "idAtencion": payload.idAtencion,
            "nomSigno": payload.nomSigno,
            "valor": payload.valor,
            "fecRegistro": payload.fecRegistro,
            }

        # inferences = await predict(data)
        port_HTTP = '5001'
        # ip = "127.0.0.1"
        ip = "127.0.0.1"
        uri = ''.join(['http://', ip, ':', port_HTTP, '/models'])
        print("Data is None: ", data is None)

        # Include the JWT token in the request headers
        headers1 = {"token": headers.get('token')}
        # headers = {"token": "asdasd"}
        # print(headers)

        try:
            # inferences = requests.post(uri, json=data, headers=headers1)
            predict_url = "http://127.0.0.1:5001"
            inferences = requests.post(predict_url + "/models",
                                       json=data, headers=headers1)
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions, such as connection errors
            raise HTTPException(status_code=503, detail="invalid operation"
                                )

        # Ensure the response is JSON serializable
        try:
            response_json = inferences.json()
        # except ValueError as e:
        except ValueError as e:
            return {"error": "Invalid JSON response from model endpoint",
                    "message": str(e)}

        return response_json
