from fastapi import FastAPI

from app.api.routes.cases import router as cases_router
from app.api.routes.search import router as search_router
from app.api.routes.locations import router as locations_router
from app.api.routes.tracking import router as tracking_router

app = FastAPI(
    title="DraftMate E-Court Service",
    version="1.0.0",
)

import httpx
from app.core.config import settings


@app.get("/debug/auth-check")
async def debug_auth_check():
    url = (
        f"{settings.auth_service_url.rstrip('/')}"
        "/verify_session/60669e0c-9337-4c19-90b5-72f959555adf"
    )

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            trust_env=False,
        ) as client:
            response = await client.get(url)
            return {
                "status_code": response.status_code,
                "reachable": True,
            }
    except httpx.RequestError as exc:
        print(
            f"DEBUG AUTH ERROR: {type(exc).__name__}: {exc!r}",
            flush=True,
        )
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="Auth diagnostic failed",
        )


app.include_router(cases_router)
app.include_router(search_router)
app.include_router(locations_router)
app.include_router(tracking_router)
