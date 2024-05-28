# Importing libraries for data processing
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")

def parse_test_report(file_path: str) -> ET.Element:
    """Parses a JaCoCo XML report and returns the root element."""
    tree = ET.parse(file_path)
    return tree.getroot()

# Create a test data object for each file
def extract_test_data(root: ET.Element) -> list:
    """Extracts test method data including coverage details from the XML root."""
    test_data = []
    for testcase in root.findall('testcase'):
        name = testcase.attrib.get('name')
        classname = testcase.attrib.get('classname')
        time = float(testcase.attrib.get('time', 0))
        failure = testcase.find('failure') is not None
        error = testcase.find('error') is not None
        test_data.append({
            'name': name,
            'classname': classname,
            'time': time,
            'failure': failure,
            'error': error
        })
    return test_data


def collect_test_data(report_dir: str) -> list:
    """ Extracts the data from all files and returns in list form for analysis """
    test_data = []
    for root, _, files in os.walk(report_dir):
        for file_name in files:
            if file_name.endswith('.xml'):
                file_path = os.path.join(root, file_name)
                root_element = parse_test_report(file_path)
                data = extract_test_data(root_element)
                test_data.append(data)
    return test_data


def analyze_test_data(test_data: list) -> pd.DataFrame:
    """ Retrieves the relevant info from the test data and creates a dataframe """
    test_runs = defaultdict(lambda: {'test_class': '','runs': 0, 'failures': 0, 'total_time': 0.0})

    for run_data in test_data:
        for test in run_data:
            test_name = f"{test['name']}"
            test_runs[test_name]['runs'] += 1
            test_runs[test_name]['test_class'] = test['classname']
            test_runs[test_name]['total_time'] += test['time']
            if test['failure'] or test['error']:
                test_runs[test_name]['failures'] += 1

    # Create a DataFrame
    test_data_df = pd.DataFrame([
        {'test_name': test_name, 'test_class': counts['test_class'], 'runs': counts['runs'], 'failures': counts['failures'], 'total_time': counts['total_time']}
        for test_name, counts in test_runs.items()
    ])

    # Calculate failure percentage for each test
    test_data_df['failure_percentage'] = (test_data_df['failures'] / test_data_df['runs']) * 100

    # Threshold percentage for flakiness
    threshold_percentage = 5  # Adjust as needed

    # Mark a test as flakey if failure percentage is > threshold
    test_data_df['flakey'] = test_data_df['failure_percentage'] > threshold_percentage
    test_data_df['avg_time'] = test_data_df['total_time'] / test_data_df['runs']

    return test_data_df

def create_github_link(row):
    """ Best attempt to add github links """
    folder_class_map = { # Did some for now
        "foundation": "foundation/test/source",
        # "cache": "lib-cache",
        "communicator": "communicator/test/source",
        "ests": "ests-pubsub/src/test/java",
        "events": "lib-events/test/java",
        "reportprocessor": "report-processor/src/test/java",
        "webapp": "gui/test/src",
        "contractorservice": "libs/communicator/contractor-service-client",
    }

    # Base URL for the GitHub repository
    base_github_url = f"https://github.com/{OWNER}/{REPO}/tree/main"
    
    location = row['test_class'].split('.')[2]
    # Replace dots in the class name with slashes to form the path
    class_path = row['test_class'].replace('.', '/')
    # Construct the GitHub URL
    return f"{base_github_url}/{folder_class_map.get(location)}/{class_path}.java"

if __name__ == "__main__":
    test_data_list = collect_test_data("./temp/")

    # Processing and analyzing data
    all_test_data = []
    for test_data_run in test_data_list:
        all_test_data.extend(test_data_run)

    test_data_df = analyze_test_data(all_test_data)

    # Add a column for GitHub links 
    test_data_df['github_link'] = test_data_df.apply(create_github_link, axis=1)

    # Export data
    test_data_df.to_csv('test_data.csv', index=False)



