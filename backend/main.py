from fastapi import FastAPI

from app.core.origins import make_middleware, init_routers
from app.core.logger import setup_logger


def create_app() -> FastAPI:
    logger = setup_logger()

    app_ = FastAPI(
        middleware=make_middleware(),
        title="Template FastAPI",
        description="Template FastAPI",
        version="V1.0",
    )

    init_routers(app_=app_)
    logger.info("FastAPI application created successfully.")
    return app_


app = create_app()
