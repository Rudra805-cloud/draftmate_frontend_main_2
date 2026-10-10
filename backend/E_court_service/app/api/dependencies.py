from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

import httpx
from fastapi import Header, HTTPException
from app.core.config import settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


async def get_current_user_id(
    authorization: str | None = Header(default=None),
) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    session_id = authorization.removeprefix("Bearer ").strip()
    if not session_id:
        raise HTTPException(status_code=401, detail="Missing session token")
    print("AUTH CHECK: starting session verification", flush=True)

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            trust_env=False,
        ) as client:
            response = await client.get(
                f"{settings.auth_service_url.rstrip('/')}/verify_session/{session_id}"
            )
            print(
                f"AUTH CHECK: response received, status={response.status_code}",
                flush=True,
            )

    # except httpx.RequestError:
    #     raise HTTPException(
    #         status_code=503,
    #         detail="Authentication service unavailable",
    #     )
    except httpx.RequestError as exc:
        print(
            f"Auth request failed: {type(exc).__name__}: {exc!r}",
            flush=True,
        )
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable",
        )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")

    try:
        data = response.json()
        user_id = str(data["user_id"]).strip()
        if data.get("valid") is not True or not user_id:
            raise ValueError("Invalid session response")
    except (ValueError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid session")

    return user_id
