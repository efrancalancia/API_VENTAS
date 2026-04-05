from fastapi import FastAPI
from routers.comprobante import router as comprobante_router

app = FastAPI(
    title="API Ventas",
    description="API para creación de comprobantes de venta en Oracle",
    version="1.0.0",
)

app.include_router(comprobante_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True)
