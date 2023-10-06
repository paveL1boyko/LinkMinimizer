import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.frameworks_and_drivers.asgi:app", reload=True)
