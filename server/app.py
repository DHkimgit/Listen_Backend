from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.router.user import router as UserRouter
from server.router.test import router as PwTestRouter
app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(PwTestRouter, tags=["Test"], prefix="/test")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}