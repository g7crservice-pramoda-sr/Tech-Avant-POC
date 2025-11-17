from fastapi import APIRouter
from fastapi.responses import RedirectResponse


root_route = APIRouter(tags=["Root"])


@root_route.get("/")
async def fn_test():
    """
    Pings to test if fastapi is running
    """
    return RedirectResponse("/docs")
