import os
import re
import secrets
import time
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import firestore
from pydantic import BaseModel

from jogi_agent.utils import get_config, initialize_firebase, format_history_for_prompt, init_deep_analysis, run_deep_analysis
from jogi_agent.router import RouterFlow


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


FASTAPI_API_SECRET = os.environ["FASTAPI_API_SECRET"]


def verify_api_secret(authorization: str | None) -> None:
    expected = f"Bearer {FASTAPI_API_SECRET}"

    if not authorization or not secrets.compare_digest(
        authorization,
        expected,
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )


class QuestionRequest(BaseModel):
    question: str
    history: list[dict[str, str]]
    da_questions: str = ""
    da_answers: str = ""
    username: str = ""
    chatID: str = ""
    questionNumber: str = ""


class LogCommentRequest(BaseModel):
    questionId: str
    correctness: Literal["like", "dislike"]
    comment: str


def format_runtime(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    return f"{minutes}m {remaining_seconds}s"


def remove_legal_references(text: str) -> str:
    pattern = (
        r"\n?###\s+JOGSZABÁLYI HIVATKOZÁSOK\b.*?(?=\n###\s|\Z)"
    )

    cleaned_text = re.sub(
        pattern,
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    return cleaned_text.strip()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/ask")
def ask(
    request: QuestionRequest,
    authorization: str | None = Header(default=None),
):
    # Csak a Vercel proxy hívhatja meg
    verify_api_secret(authorization)

    config = get_config()

    inputs = {
        "topic": request.question,
        "details": "",
        "history": format_history_for_prompt(request.history),
        "da_questions": request.da_questions or "",
        "da_answers": request.da_answers or "",
        'username': request.username or "U_2",
        "chatID": request.chatID or "",
        "questionNumber": request.questionNumber or "0"
    }

    flow = RouterFlow()

    flow.state["inputs"] = inputs

    start = time.perf_counter()

    response = flow.kickoff()

    runtime = time.perf_counter() - start

    questonId = flow.get_question_id()
    chatId = flow.get_chat_id()
    history = flow.get_history()

    return {
        "answer": remove_legal_references(str(response)),
        "paragraphs": str(flow.get_chunks()),
        "runtime": format_runtime(runtime),
        "chat_id": chatId,
        "question_id": questonId,
        "history": history
    }

@app.post("/api/v1/askDeepAnalysis")
def askDeepAnalysis(
    request: QuestionRequest,
    authorization: str | None = Header(default=None),
):
    # Csak a Vercel proxy hívhatja meg
    verify_api_secret(authorization)

    config = get_config()

    start = time.perf_counter()
    tasks_config, da_agent = init_deep_analysis(is_verbose=False)
    da_questions = run_deep_analysis(tasks_config, request.question, format_history_for_prompt(request.history), da_agent)
    runtime = time.perf_counter() - start

    return {
        "questions": da_questions,
        "runtime": format_runtime(runtime)
    }

@app.post("/api/v1/comment")
def comment(
    request: LogCommentRequest,
    authorization: str | None = Header(default=None),
):
    verify_api_secret(authorization)

    db = initialize_firebase()

    feedback = {
        "questionId": request.questionId,
        "correctness": request.correctness,
        "comment": request.comment,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    _, doc_ref = db.collection("feedback").add(feedback)

    return {
        "success": True,
        "id": doc_ref.id,
    }
