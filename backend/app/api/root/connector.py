from fastapi import APIRouter
from fastapi.responses import JSONResponse


root_route = APIRouter(tags=["Root"])


@root_route.get("/")
async def fn_test():
    """
    Pings to test if fastapi is running
    """
    return JSONResponse({"message": "success"})
