""" Company research agent definition"""

import warnings

warnings.filterwarnings("ignore", message=".*TqdmWarning.*")
from dotenv import load_dotenv

_ = load_dotenv()

import operator
import os
from typing import Annotated, List, TypedDict

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from prompts import RESEARCH_PLAN_PROMPT, WRITER_PROMPT
from pydantic import BaseModel
from tavily import TavilyClient


class AgentState(TypedDict):
    task: str
    lnode: str
    plan: str
    draft: str
    content: List[str]
    queries: List[str]
    count: Annotated[int, operator.add]


class Queries(BaseModel):
    queries: List[str]


class CompanyInfo(BaseModel):
    company_name: str
    industry: str
    city: str
    country: str
    number_of_employees: int
    company_description: str
    company_website: str


class eresearcher:
    def __init__(self):

        # Initialize the model and the Tavily client
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

        # Define the prompts
        self.WRITER_PROMPT = WRITER_PROMPT
        self.RESEARCH_PLAN_PROMPT = RESEARCH_PLAN_PROMPT

        # Create the graph
        # Nodes
        builder = StateGraph(AgentState)
        builder.add_node("research_plan", self.research_plan_node)
        builder.add_node("generate", self.generation_node)
        builder.set_entry_point("research_plan")
        # Edges
        builder.add_edge("research_plan", "generate")
        builder.add_edge("generate", END)

        # Compile graph with memory and interrupt states
        checkpointer = MemorySaver()
        self.graph = builder.compile(
            checkpointer=checkpointer,
        )

    # Node definitions

    def research_plan_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke(
            [
                SystemMessage(content=self.RESEARCH_PLAN_PROMPT),
                HumanMessage(content=state["task"]),
            ]
        )
        content = state.get("content", [])  # add to content
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response["results"]:
                content.append(r["content"])
        return {
            "content": content,
            "queries": queries.queries,
            "lnode": "research_plan",
            "count": 1,
        }

    def generation_node(self, state: AgentState):
        content = "\n\n".join(state["content"] or [])
        messages = [
            SystemMessage(content=self.WRITER_PROMPT.format(content=content)),
        ]
        response = self.model.with_structured_output(CompanyInfo).invoke(messages)
        return {
            "draft": response,
            "lnode": "generate",
            "count": 1,
        }
