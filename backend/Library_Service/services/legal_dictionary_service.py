# async def search_terms_service(
#     pool,
#     query: str,
#     page: int,
#     limit: int,
# ):
#     normalized_query = query.strip().lower()
#     offset = (page - 1) * limit

#     async with pool.acquire() as connection:
#         total = await connection.fetchval(
#             """
#             SELECT COUNT(*)
#             FROM legal_terms
#             WHERE status = 'active'
#               AND (
#                   normalized_term = $1
#                   OR similarity(normalized_term, $1) >= 0.2
#               )
#             """,
#             normalized_query,
#         )

#         rows = await connection.fetch(
#             """
#             SELECT
#                 id,
#                 term,
#                 CASE
#                     WHEN normalized_term = $1 THEN 'EXACT'
#                     ELSE 'SIMILAR'
#                 END AS "matchType"
#             FROM legal_terms
#             WHERE status = 'active'
#               AND (
#                   normalized_term = $1
#                   OR similarity(normalized_term, $1) >= 0.2
#               )
#             ORDER BY
#                 CASE
#                     WHEN normalized_term = $1 THEN 0
#                     ELSE 1
#                 END,
#                 similarity(normalized_term, $1) DESC
#             LIMIT $2 OFFSET $3
#             """,
#             normalized_query,
#             limit,
#             offset,
#         )

#     return {
#         "items": [dict(row) for row in rows],
#         "total": total,
#         "page": page,
#         "limit": limit,
#     }


# async def get_term_service(pool, term_id: int):
#     async with pool.acquire() as connection:
#         row = await connection.fetchrow(
#             """
#             SELECT
#                 id,
#                 term,
#                 normalized_term,
#                 explanation,
#                 status,
#                 created_at,
#                 updated_at
#             FROM legal_terms
#             WHERE id = $1
#             """,
#             term_id,
#         )

#     return dict(row) if row else None
from sqlalchemy import text


def search_terms_service(
    db,
    query: str,
    page: int,
    limit: int,
):
    normalized_query = query.strip().lower()
    offset = (page - 1) * limit

    total = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM legal_terms
            WHERE status = 'active'
              AND (
                  normalized_term = :query
                  OR similarity(normalized_term, :query) >= 0.2
              )
            """
        ),
        {"query": normalized_query},
    ).scalar()

    rows = (
        db.execute(
            text(
                """
            SELECT
                id,
                term,
                CASE
                    WHEN normalized_term = :query THEN 'EXACT'
                    ELSE 'SIMILAR'
                END AS "matchType"
            FROM legal_terms
            WHERE status = 'active'
              AND (
                  normalized_term = :query
                  OR similarity(normalized_term, :query) >= 0.2
              )
            ORDER BY
                CASE
                    WHEN normalized_term = :query THEN 0
                    ELSE 1
                END,
                similarity(normalized_term, :query) DESC
            LIMIT :limit OFFSET :offset
            """
            ),
            {
                "query": normalized_query,
                "limit": limit,
                "offset": offset,
            },
        )
        .mappings()
        .all()
    )

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit,
    }


def get_term_service(db, term_id: int):
    row = (
        db.execute(
            text(
                """
            SELECT
                id,
                term,
                normalized_term,
                explanation,
                status,
                created_at,
                updated_at
            FROM legal_terms
            WHERE id = :term_id
            """
            ),
            {"term_id": term_id},
        )
        .mappings()
        .first()
    )

    return dict(row) if row else None
