from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from agent import DispatchAgent
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to Humonos"}


if __name__ == "__main__":
    agent = DispatchAgent("gpt-4o-mini", str(os.getenv("OPENAI_KEY")))

    agent()
    pass
    # import uvicorn

    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
