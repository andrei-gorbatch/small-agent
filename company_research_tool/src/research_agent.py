"""Script to process a list of companies using the agent and save the results to a CSV file"""
import warnings

import pandas as pd
from agent import eresearcher

warnings.filterwarnings("ignore")


def read_companies(filepath):
    """Function to read company names from a CSV file"""
    companies = pd.read_csv(filepath)
    return companies["Company Name"].tolist()


def process_company(company, thread_id, agent):
    """Function to process a single company using the agent"""
    print(f"Processing {company}")
    thread = {"configurable": {"thread_id": f"{thread_id}"}}
    result = agent.graph.invoke(
        {
            "task": company,
        },
        thread,
    )
    try:
        return result.get("draft").dict()
    except Exception as e:
        print(f"Skipping {company}: {e}")
        return None


def save_data(data, filepath):
    """Function to save the processed data to a CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)


def main():
    """Main function to process the list of companies. Saves the data to a CSV file"""

    # Read the list of companies from input csv file
    filepath = "company_research_tool/data/companies.csv"
    output_filepath = "company_research_tool/data/companies_data.csv"
    companies = read_companies(filepath)

    # Initialize the agent
    agent = eresearcher()
    list_of_companies = []

    # Process each company and collect the results
    for thread_id, company in enumerate(companies, start=1):
        company_data = process_company(company, thread_id, agent)
        if company_data:
            list_of_companies.append(company_data)

    # Save the collected data to a CSV file
    save_data(list_of_companies, output_filepath)


if __name__ == "__main__":
    main()
