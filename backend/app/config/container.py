# app/config/container.py

from __future__ import annotations
from dataclasses import dataclass

from app.config.settings import settings

# Repos
from app.repositories.patient_repo import PatientRepository
from app.repositories.chat_memory_repo import InMemoryChatRepository

# Vector store + retriever
from app.stores.chroma_store import ChromaVectorStore
from app.retrieval.ng12_retriever import NG12Retriever

# Providers / policy
from app.providers.llm_provider import LLMProvider
from app.policy.assessment_policy import AssessmentPolicy

# Graphs
from app.agents.assessor_graph import build_assessor_graph
from app.agents.chat_graph import build_chat_graph

# Services
from app.services.assessor_service import AssessorService
from app.services.chat_service import ChatService


@dataclass
class Container:
    """
    Dependency injection container.
    Creates and owns all singletons.
    """

    store: ChromaVectorStore | None = None
    retriever: NG12Retriever | None = None
    llm: LLMProvider | None = None

    patients: PatientRepository | None = None
    memory: InMemoryChatRepository | None = None

    policy: AssessmentPolicy | None = None

    assessor_graph: object | None = None
    chat_graph: object | None = None

    assessor_service: AssessorService | None = None
    chat_service: ChatService | None = None

    def __post_init__(self) -> None:
        # 1) Vector store (uses settings internally)
        self.store = ChromaVectorStore()

        # 2) Retriever ✅ CORRECT ARGUMENTS
        self.retriever = NG12Retriever(
            store=self.store,
            embedding_provider=settings.EMBEDDING_MODEL,
            top_k_default=settings.DEFAULT_TOP_K,
        )

        # 3) LLM provider
        self.llm = LLMProvider(
            model=settings.LLM_MODEL,
            project=settings.GCP_PROJECT,
            location=settings.GCP_LOCATION,
        )

        # 4) Repositories
        self.patients = PatientRepository(
            data_path=str(settings.PATIENTS_PATH)
        )
        self.memory = InMemoryChatRepository()

        # 5) Policy
        self.policy = AssessmentPolicy(
            min_top_score=settings.MIN_TOP_SCORE
        )

        # 6) Graphs (AGENTIC FLOW)
        self.assessor_graph = build_assessor_graph(
            patient_repo=self.patients,
            retriever=self.retriever,
            llm=self.llm,
            policy=self.policy,
        )

        self.chat_graph = build_chat_graph(
            memory_store=self.memory,
            retriever=self.retriever,
            llm=self.llm,
        )

        # 7) Services
        self.assessor_service = AssessorService(self.assessor_graph)
        self.chat_service = ChatService(self.chat_graph, self.memory)
