# app/main.py

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.container import Container
from app.api.chat import router as chat_router
from app.api.assess import router as assess_router
from app.api.debug import router as debug_router


def create_app() -> FastAPI:
    app = FastAPI(title="NG12 Clinical Agent", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.container = Container()

    app.include_router(assess_router)
    app.include_router(chat_router)
    app.include_router(debug_router)

    return app


app = create_app()
