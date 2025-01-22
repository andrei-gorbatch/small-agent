import openai
import re
import httpx
import os
import json

from openai import OpenAI
from search import google_search, get_text_from_url, get_csv_links_from_url
from python_code import execute_python_code, download_csv_from_url
from dotenv import load_dotenv

_ = load_dotenv()

client = OpenAI()

# Add known actions
known_actions = {
    "google_search": google_search,
    "execute_python_code": execute_python_code,
    "download_webpage": get_text_from_url,
    "find_csv_links": get_csv_links_from_url,
    "download_csv_from_url": download_csv_from_url
}

# Agent prompt
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

google_search:
e.g. google_search: list of EU companies
Does a google search and returns relevant information

download_webpage: 
e.g. download_webpage: https://epoch.ai/data/notable-ai-models
Returns the text content of the webpage

find_csv_links:
e.g. find_csv_links: https://epoch.ai/data/notable-ai-models
Returns a list of links to csv files on the webpage. Some web pages have information available in a csv file. Use it to find the csv file you want to download

download_csv_from_url:
e.g. download_csv_from_url: https://epoch.ai/data/epochdb/notable_ai_models.csv
Downloads the csv file from the url and saves it to the current directory with the name data.csv. If the url is invalid, returns an error message

execute_python_code:
e.g. execute_python_code: print("Hello, World!")
Executes the python code and returns the output. If the code is invalid, returns an error message
Example usage: execute_python_code("print('hello world')")

Example session:

Question: Find all UK companies that have a revenue over 1 billion pounds in 2023?
Thought: I should look for the list of all big UK companies
Action: google_search: list of big UK companies 
PAUSE

You will be called again with this:

Observation: {'https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_Kingdom': 'This article lists the largest companies in the United Kingdom in terms of their revenue, net profit and total assets, according to the American business ...',
 'https://builtin.com/articles/uk-largest-companies': "UK's Largest Companies · Klaviyo · Navan · Shell Plc · Smartly · AVEVA · NBCUniversal · Kraft Heinz · Hsbc Bank Usa, N.A..",
 'https://companiesmarketcap.com/united-kingdom/largest-companies-in-the-uk-by-market-cap/': 'List of the largest UK companies by market capitalization, all rankings are updated daily.',}
You then output:

Thought: I should download the text content of the wikipedia page to find the list of all big UK companies
Action: download_webpage: https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_Kingdom
PAUSE

You will be called again with this:
Observation: '\n\n\n\nList of largest companies in the United Kingdom - Wikipedia\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nJump to content\n\n\n\n\n\n\n\nMain menu\n\n\n\n\n\nMain menu\nmove to sidebar\nhide\n\n\n\n\t\tNavigation\n\t\n\n\nMain pageContentsCurrent eventsRandom articleAbout WikipediaContact us\n\n\n\n\n\n\t\tContribute\n\t\n\n\nHelpLearn to editCommunity portalRecent changesUpload file\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSearch\n\n\n\n\n\n\n\n\n\n\n\nSearch\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nAppearance\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nDonate\n\nCreate account\n\nLog in\n\n\n\n\n\n\n\n\nPersonal tools\n\n\n\n\n\nDonate Create account Log in\n\n\n\n\n\n\t\tPages for logged out editors learn more\n\n\n\nContributionsTalk\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nContents\nmove to sidebar\nhide\n\n\n\n\n(Top)\n\n\n\n\n\n1\n2024 Fortune 500:\n\n\n\n\n\n\n\n\n2\n2024 Forbes list\n\n\n\n\n\n\n\n\n3\nSee also\n\n\n\n\n\n\n\n\n4\nReferences\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nToggle the table of contents\n\n\n\n\n\n\n\nList of largest companies in the United Kingdom\n\n\n\n3 languages\n\n\n\n\nالعربيةDeutschPortuguês\n\nEdit links\n\n\n\n\n\n\n\n\n\n\n\nArticleTalk\n\n\n\n\n\nEnglish\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nReadEditView history\n\n\n\n\n\n\n\nTools\n\n\n\n\n\nTools\nmove to sidebar\nhide\n\n\n\n\t\tActions\n\t\n\n\nReadEditView history\n\n\n\n\n\n\t\tGeneral\n\t\n\n\nWhat links hereRelated changesUpload fileSpecial pagesPermanent linkPage informationCite this pageGet shortened URLDownload QR code\n\n\n\n\n\n\t\tPrint/export\n\t\n\n\nDownload as PDFPrintable version\n\n\n\n\n\n\t\tIn other projects\n\t\n\n\nWikidata item\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nAppearance\nmove to sidebar\nhide\n\n\n\n\n\n\n\n\n\n\nFrom Wikipedia, the free encyclopedia\n\n\n\nThis article lists the largest companies in the United Kingdom in terms of their revenue, net profit and total assets, according to the American business magazines Fortune and Forbes.\n\n\n2024 Fortune 500:[edit]\nThis list displays all British companies in the Fortune Global 500, which ranks the world\'s largest companies by annual revenue. The figures below are given in millions of US dollars and are for the fiscal year 2023/24. Also listed are the headquarters location, net profit, number of employees worldwide and industry sector of each company.[1]\n\n\n\nRank\n\nFortune 500rank\n\nName\n\nIndustry\n\nRevenue(USD millions)\n\nProfits(USD millions)\n\nAssets(USD millions)\n\nEmployees\n\nHeadquarters\n\n\n 1\n\n 13\n\nShell plc\n\nOil and Gas\n\n 323,183\n\n 19,359\n\n406,270\n\n103,000\n\nLondon\n\n\n 2\n\n 25\n\nBP\n\nOil and Gas\n\n 213,032\n\n 15,239\n\n280,294\n\n79,400\n\nLondon\n\n\n 3\n\n 67\n\nHSBC\n\nBanking\n\n 134,901\n\n 23,533\n\n3,038,677\n\n220,861\n\nLondon\n\n\n 4\n\n 140\n\n\nSee also[edit]\nList of companies of the United Kingdom\nList of largest private companies in the United Kingdom\nList of largest companies by revenue\nList of largest private non-governmental companies by revenue\nReferences[edit]\n\n\n^ "Global 500". Fortune. Retrieved 2022-08-28.\n\n^ Murphy, Andrea; Contreras, Isabel. "The Global 2000". Forbes. Retrieved 2022-08-28.\n\n\n\n\n\n\nRetrieved from "https://en.wikipedia.org/w/index.php?title=List_of_largest_companies_in_the_United_Kingdom&oldid=1270056181"\nCategories: Lists of largest private companies by countryEconomy of the United Kingdom-related listsWealth in the United KingdomLists of companies of the United KingdomUnited Kingdom-related lists of superlativesHidden categories: Articles with short descriptionShort description is different from Wikidata\n\n\n\n\n\n\n This page was last edited on 17 January 2025, at 18:22\xa0(UTC).\nText is available under the Creative Commons Attribution-ShareAlike 4.0 License;\nadditional terms may apply. By using this site, you agree to the Terms of Use and Privacy Policy. Wikipedia® is a registered trademark of the Wikimedia Foundation, Inc., a non-profit organization.\n\n\nPrivacy policy\nAbout Wikipedia\nDisclaimers\nContact Wikipedia\nCode of Conduct\nDevelopers\nStatistics\nCookie statement\nMobile view\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSearch\n\n\n\n\n\n\n\n\n\n\n\n\n\nSearch\n\n\n\n\n\n\n\n\n\nToggle the table of contents\n\n\n\n\n\n\n\nList of largest companies in the United Kingdom\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n3 languages\n\n\nAdd topic\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'


Thought: I should check if this information is available in a csv file
Action: find_csv_links: https://en.wikipedia.org/wiki/List_of_largest_companies_in_the_United_Kingdom
PAUSE

You will be called again with this:
Observation: ["No CSV links found on the page"]

Thought: No csv file is available, so use text from the webpage instead. Largest companies listed are Shell plc, BP, HSBC. I should search for the revenue of these companies. I will start with Shell plc.
Action: google_search: revenue of Shell plc in 2023
PAUSE

You will be called again with this:
Observation: Shell plc revenue in 2023: 1.2 billion pounds
You then output:

Thought: Shell plc has a revenue of 1.2 billion pounds in 2023. I will search for BP next.
Action: google_search: revenue of BP in 2023
PAUSE

You will be called again with this:
Observation: BP revenue in 2023: 0.9 billion pounds
You then output:

Thought: Shell plc has a revenue of 1.2 billion pounds in 2023, BP revenue is 0.9 billion pounds. I will search for HSBC next.
Action: google_search: revenue of HSBC in 2023
PAUSE

You will be called again with this:
Observation: HSBC revenue in 2023: 0.8 billion pounds
You then output:

Thought: Shell plc has a revenue of 1.2 billion pounds in 2023, BP revenue is 0.9 billion pounds, HSBC  as a revenue of 0.8 billion pounds. I will write python code to filter out companies with revenue over 1 billion pounds.
Action: execute_python_code: companies = ["Shell plc", "BP", "HSBC"]; revenues = [1.2, 0.9, 0.8]; big_companies = [company for company, revenue in zip(companies, revenues) if revenue > 1]; big_companies
PAUSE

You will be called again with this:
Observation: ['Shell plc']
You then output:

Answer: Shell plc is the only UK company with a revenue over 1 billion pounds in 2023. 

""".strip()


# Define simple Agent class
class Agent:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
            model="gpt-4o", temperature=0, messages=self.messages
        )
        return completion.choices[0].message.content
    

abot = Agent(prompt)
action_re = re.compile(
    "^Action: (\w+): (.*)$"
)  # python regular expression to selection action

def process_task(question, max_turns=10):
    i = 0
    bot = Agent(prompt)
    next_prompt = question
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [action_re.match(a) for a in result.split("\n") if action_re.match(a)]
        if actions:
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input))
            print(" -- running {} {}".format(action, action_input))
            observation = known_actions[action](action_input)
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            return result