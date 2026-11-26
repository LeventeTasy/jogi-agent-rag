import os
from typing import Type
from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools import BaseTool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from rag import build_rag, query_rag


class JogiKeresoInput(BaseModel):
    """Input schema for MyCustomTool."""
    query: str = Field(..., description="A jogi kérdés vagy keresőszavak.")


class RagTool(BaseTool):
    name: str = "Jogi adatbázis"
    description: str = (
        "Használd ezt a toolt, ha a Munka Törvénykönyve, Ptk vagy GDPR kapcsán kell keresned."
    )
    args_schema: Type[BaseModel] = JogiKeresoInput
    _db: Chroma = PrivateAttr()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #build_rag()

        # Elérési út, embeddings beállítása
        db_path = os.path.abspath(os.path.join(os.getcwd(), "chroma_db"))
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # Mentés a belső _db változóba
        self._db = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings
        )
        print("--- RAG Adatbázis sikeresen betöltve a memóriába! ---")
        print(f"DB PATH: {db_path}")
        print(f"DB COUNT: {self._db._collection.count()}")

    def _run(self, query: str) -> str:
        print("Tool started")
        formatted_context, source_list, chunks = query_rag(query, self._db)

        return formatted_context