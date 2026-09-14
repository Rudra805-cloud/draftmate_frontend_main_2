# from fastapi import APIRouter, Depends, HTTPException, Query, status

# from database import get_db

# # change karna hai
# from Li import (
#     get_term_controller,
#     search_terms_controller,
# )
# from app.schemas.legal_dictionary_schema import (
#     TermDetailResponse,
#     TermSearchPaginatedResponse,
# )

# router = APIRouter(
#     prefix="/api/v1/library/terms",
#     tags=["Legal Dictionary"],
# )


# @router.get(
#     "/",
#     response_model=TermSearchPaginatedResponse,
# )
# async def search_terms(
#     pool=Depends(get_db_pool),
#     query: str = Query(..., min_length=1),
#     page: int = Query(1, ge=1),
#     limit: int = Query(20, ge=1, le=100),
# ):
#     return await search_terms_controller(
#         pool=pool,
#         query=query,
#         page=page,
#         limit=limit,
#     )


# @router.get(
#     "/{term_id}",
#     response_model=TermDetailResponse,
# )
# async def get_term(
#     term_id: int,
#     pool=Depends(get_db_pool),
# ):
#     term = await get_term_controller(
#         pool=pool,
#         term_id=term_id,
#     )

#     if term is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Legal term not found",
#         )

#     return term
from fastapi import APIRouter, Depends, HTTPException, Query, status

from database import get_db

print("LEGAL DICTIONARY ROUTER LOADED")

from controllers.legal_dictionary_controller import (
    get_term_controller,
    search_terms_controller,
)

from schemas import (
    TermDetailResponse,
    TermSearchPaginatedResponse,
)


router = APIRouter(
    prefix="/api/v1/library/terms",
    tags=["Legal Dictionary"],
)


@router.get(
    "",
    response_model=TermSearchPaginatedResponse,
)
def search_terms(
    db=Depends(get_db),
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    return search_terms_controller(
        db=db,
        query=query,
        page=page,
        limit=limit,
    )


@router.get(
    "/{term_id}",
    response_model=TermDetailResponse,
)
def get_term(
    term_id: int,
    db=Depends(get_db),
):
    term = get_term_controller(
        db=db,
        term_id=term_id,
    )

    if term is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Legal term not found",
        )

    return term
