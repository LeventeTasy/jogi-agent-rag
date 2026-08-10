from fastapi import FastAPI
from jogi_agent.utils import get_config
from pydantic import BaseModel
from jogi_agent.flow import JogiFlow
from jogi_agent.crew import JogiAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str


@app.post("/api/v1/ask")
def ask(request: QuestionRequest):
    config = get_config()
    is_memory = config["is_memory"]

    inputs = {
        'topic': request.question,
        'details': ""
    }

    flow = JogiFlow()

    if is_memory:
        JogiAgent().crew().reset_memories(command_type="memory")

    flow.state["inputs"] = inputs

    response = flow.kickoff()

    return {
        "answer": str(response)
    }