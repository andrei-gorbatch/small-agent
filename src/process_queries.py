# File to process queries and return the results. 
# Your entrypoint script should take a path to a text file with a task on every line, and should run your agent on the tasks in the file and write out the results.

import os
import sys

from agent import process_task

def process_queries(file_path):
    with open(file_path, 'r') as file:
        tasks = file.readlines()
    
    task_result_pairs = []

    for task in tasks:
        result = process_task(task)
        task_result_pairs.append((task.strip(), result))

    # Write the results to a file
    with open("results.txt", 'w') as file:
        for task, result in task_result_pairs:
            file.write(f"Task: {task} - Result: {result}\n")

if __name__ == "__main__":
    file_path = "tasks.txt"
    process_queries(file_path)