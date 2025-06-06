from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_roof():
    return {"message": "Hello World"}


if __name__ == "__main__":
    ...
