from fastapi import FastAPI

from app.api.routes.cases import router as cases_router
from app.api.routes.search import router as search_router
from app.api.routes.locations import router as locations_router
from app.api.routes.tracking import router as tracking_router

app = FastAPI(
    title="DraftMate E-Court Service",
    version="1.0.0",
)


app.include_router(cases_router)
app.include_router(search_router)
app.include_router(locations_router)
app.include_router(tracking_router)
