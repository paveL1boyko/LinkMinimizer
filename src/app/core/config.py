from os import environ as env


class Config:
    RETRY_COUNT_TO_CREATE_UNIQUE_SHORT_CODE = int(
        env.get("RETRY_COUNT_TO_CREATE_UNIQUE_SHORT_CODE", 5)
    )
    REDIS_CACHE_URL = env.get("REDIS_CACHE_URL", "redis://localhost")
    MONGODB_DB_URL = env.get(
        "MONGODB_DB_URL",
        "mongodb://root:example@localhost:27017",
    )
    LINK_MINIMIZER_DB_NAME = "link_minimizer"
    CACHE_TIME = env.get("CACHE_TIME", 3600)
