import re
import time

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

def format_runtime(seconds):
    if seconds < 60:
        return f"{seconds:.0f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    return f"{minutes}m {remaining_seconds}s"

def remove_legal_references(text: str) -> str:
    pattern = r"\n?###\s+JOGSZABÁLYI HIVATKOZÁSOK\b.*?(?=\n###\s|\Z)"

    cleaned_text = re.sub(
        pattern,
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    return cleaned_text.strip()

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

    start = time.perf_counter()
    response = flow.kickoff()
    runtime = time.perf_counter() - start

    return {
        "answer": remove_legal_references(str(response)),
        "paragraphs": str(flow.get_chunks()),
        "runtime": format_runtime(runtime)
    }