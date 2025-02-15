""" Essay writer agent definition"""

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
from prompts import (
    PLAN_PROMPT,
    REFLECTION_PROMPT,
    RESEARCH_CRITIQUE_PROMPT,
    RESEARCH_PLAN_PROMPT,
    WRITER_PROMPT,
)
from pydantic import BaseModel
from tavily import TavilyClient


class AgentState(TypedDict):
    task: str
    lnode: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    queries: List[str]
    revision_number: int
    max_revisions: int
    count: Annotated[int, operator.add]


class Queries(BaseModel):
    queries: List[str]


class ewriter:
    def __init__(self):

        # Initialize the model and the Tavily client
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

        # Define the prompts
        self.PLAN_PROMPT = PLAN_PROMPT
        self.WRITER_PROMPT = WRITER_PROMPT
        self.RESEARCH_PLAN_PROMPT = RESEARCH_PLAN_PROMPT
        self.REFLECTION_PROMPT = REFLECTION_PROMPT
        self.RESEARCH_CRITIQUE_PROMPT = RESEARCH_CRITIQUE_PROMPT

        # Create the graph
        # Nodes
        builder = StateGraph(AgentState)
        builder.add_node("planner", self.plan_node)
        builder.add_node("research_plan", self.research_plan_node)
        builder.add_node("generate", self.generation_node)
        builder.add_node("reflect", self.reflection_node)
        builder.add_node("research_critique", self.research_critique_node)
        builder.set_entry_point("planner")
        # Edges
        builder.add_conditional_edges(
            "generate", self.should_continue, {END: END, "reflect": "reflect"}
        )
        builder.add_edge("planner", "research_plan")
        builder.add_edge("research_plan", "generate")
        builder.add_edge("reflect", "research_critique")
        builder.add_edge("research_critique", "generate")

        # Compile graph with memory and interrupt states
        checkpointer = MemorySaver()
        self.graph = builder.compile(
            checkpointer=checkpointer,
            interrupt_after=[
                "planner",
                "generate",
                "reflect",
                "research_plan",
                "research_critique",
            ],
        )

    # Node definitions

    def plan_node(self, state: AgentState):
        messages = [
            SystemMessage(content=self.PLAN_PROMPT),
            HumanMessage(content=state["task"]),
        ]
        response = self.model.invoke(messages)
        return {
            "plan": response.content,
            "lnode": "planner",
            "count": 1,
        }

    def research_plan_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke(
            [
                SystemMessage(content=self.RESEARCH_PLAN_PROMPT),
                HumanMessage(content=state["task"]),
            ]
        )
        content = state["content"] or []  # add to content
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
        user_message = HumanMessage(
            content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}"
        )
        messages = [
            SystemMessage(content=self.WRITER_PROMPT.format(content=content)),
            user_message,
        ]
        response = self.model.invoke(messages)
        return {
            "draft": response.content,
            "revision_number": state.get("revision_number", 1) + 1,
            "lnode": "generate",
            "count": 1,
        }

    def reflection_node(self, state: AgentState):
        messages = [
            SystemMessage(content=self.REFLECTION_PROMPT),
            HumanMessage(content=state["draft"]),
        ]
        response = self.model.invoke(messages)
        return {
            "critique": response.content,
            "lnode": "reflect",
            "count": 1,
        }

    def research_critique_node(self, state: AgentState):
        queries = self.model.with_structured_output(Queries).invoke(
            [
                SystemMessage(content=self.RESEARCH_CRITIQUE_PROMPT),
                HumanMessage(content=state["critique"]),
            ]
        )
        content = state["content"] or []
        for q in queries.queries:
            response = self.tavily.search(query=q, max_results=2)
            for r in response["results"]:
                content.append(r["content"])
        return {
            "content": content,
            "lnode": "research_critique",
            "count": 1,
        }

    # Conditional edge definition
    def should_continue(self, state):
        if state["revision_number"] > state["max_revisions"]:
            return END
        return "reflect"
