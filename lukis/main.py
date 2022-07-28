from fastapi import FastAPI

from .api import router

app = FastAPI(title="Lukis API")
app.include_router(router, prefix="/api")

@app.get("/")
def index():
    return {"message": "Welcome to Lukis"}
