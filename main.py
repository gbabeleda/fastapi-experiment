from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_roof():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fastapi-experiment"}


if __name__ == "__main__":
    ...
