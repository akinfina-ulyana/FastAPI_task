from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.routers import auth as auth_router
from app.routers import transactions as transaction_router
from app.routers import user as user_router


app = FastAPI()
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(transaction_router.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7999, reload=True)
