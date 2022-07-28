from fastapi import FastAPI

from .api import router
from .utils import setup_logging


setup_logging()

app = FastAPI(title="Lukis API")
app.include_router(router, prefix="/api")

@app.get("/")
def index():
    return {"message": "Welcome to Lukis"}
