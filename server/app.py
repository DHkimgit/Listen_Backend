# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from server.router.user import router as UserRouter
# from server.router.unit_lagecy import router as UnitLRouter
# from server.router.unit import router as UnitRouter
# from server.router.login import router as LoginRouter
# app = FastAPI()

# origins = [
#     '*'
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(UserRouter, tags=["User"], prefix="/user")
# app.include_router(UnitRouter, tags=["Unit"], prefix="/unit")
# app.include_router(LoginRouter, tags=["Login"], prefix="/login

# @app.get("/", tags=["Root"])
# async def read_root():
#     return {"message": "Welcome to this fantastic app!"}