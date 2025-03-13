# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from .database import engine, Base
# from .routes import invoices

# # Create all database tables on startup
# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(invoices.router)

# @app.get("/")
# def read_root():
#     return {"message": "Invoice Processing API"}


# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import invoices, ml  # <-- import your new route

from .database import engine, Base
from .database import Base, engine

# This is destructive! It drops all tables in your database.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# existing routers
app.include_router(invoices.router)

# new ML router
app.include_router(ml.router)

@app.get("/")
def read_root():
    return {"message": "Invoice Processing API with fraud detection"}

