# Small Agent

This repository contains several small agents:
1. agent_pure_python - A basic search agent using pure Python (no extra frameworks).
2. essay_writer_agent - LangGraph REACT agent that writes an essay about a given topic using web search. Gradio GUI is included.
3. company_research_tool - LangGraph agent that processes a list of companies to find relevant information such as industry and location, and saves it in a csv. 

## Agents

### agent_pure_python
A basic search agent using pure Python (no extra frameworks).

### essay_writer_agent
Contains an agent that writes an essay about a given topic in a few steps:

1. Create a research plan.
2. Do an internet search according to the plan.
3. Write a draft.
4. Critique the draft.
5. Repeat steps 3-4 for a fixed number of iterations (currently 3).

At any stage, human-in-the-loop interaction is possible: after each step, the agent can be interrupted, and any output updated. Several different conversations are possible by using different threads.

A GUI (gradio app) is provided to easily interact with the agent.

#### Launch Instructions

To launch, follow these steps:

1. Add a `.env` file with the required API keys.
2. Install the Poetry environment.
3. Run the GUI from `use_gui.ipynb` or `use_gui.py`.

### company_research_tool
Contains an agent that processes a list of companies to extract relevant information such as industry, location, number of employees, and a short description. The agent performs the following steps:
1. Create a research plan.
2. Do an internet search according to the plan.
3. Extract and compile the information in a csv.

#### Launch Instructions

To launch, follow these steps:

1. Add a `.env` file with the required API keys.
2. Install the Poetry environment.
3. Add a companies.csv file with a list of companies, header: Company Name.
4. Run the script from `research_agent.py` or `research_agent.ipynb`.
