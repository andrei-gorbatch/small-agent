import warnings

warnings.filterwarnings("ignore")

from agent import ewriter
from gui import writer_gui

# Use the GUI
MultiAgent = ewriter()
app = writer_gui(MultiAgent.graph)
app.launch()
