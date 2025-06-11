from fastapi import FastAPI
from routers import predict

app = FastAPI(title="StAI- Stock Prediction API",
            description="Predict Stock Prices",
            version="1.0.0")

app.include_router(predict.router)

@app.get("/")
async def root():
    return {"message":"StAI - Stock Prediction made easy"}

