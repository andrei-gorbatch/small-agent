# Small Agent

This repository contains several small agents.

## Agents

### agent_pure_python
Builds a basic search agent using pure Python (no extra frameworks).

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