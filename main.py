from fastapi import FastAPI, Depends, HTTPException
from services.firestore_services import FirestoreService, get_firestore_service
from schemas import FormData
import uvicorn

app = FastAPI()

# Ruta de verificación
@app.get("/")
async def root():
    return {"message": "API is working correctly"}

# También puedes agregar una ruta específica para chequeo de salud
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/submit-form")
async def submit_form(data: FormData, firestore_service: FirestoreService = Depends(get_firestore_service)):
    try:
        result = firestore_service.save_form_data(data)
        return {"status": "success", "message": "Data saved successfully", "data_id": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
