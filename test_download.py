import os
import requests
import zipfile
from dotenv import load_dotenv
import shutil

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError("TOKEN environment variable is not set. Please set it in the .env file.")

OWNER = os.getenv("OWNER")
REPO = os.getenv("REPO")
START_TIME = os.getenv("START_TIME")
END_TIME = os.getenv("END_TIME")
DESTINATION_DIR_ZIPS = os.getenv("DESTINATION_DIR_ZIPS")
DESTINATION_DIR_DATA = os.getenv("DESTINATION_DIR_DATA")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

# Create the destination directories if they don't exist
os.makedirs(DESTINATION_DIR_ZIPS, exist_ok=True)
os.makedirs(DESTINATION_DIR_DATA, exist_ok=True)

# Ensure the destination directories are writable
os.chmod(DESTINATION_DIR_ZIPS, 0o777)
os.chmod(DESTINATION_DIR_DATA, 0o777)

# Function to fetch all workflow runs and handle pagination
def fetch_runs(url, headers):
    all_run_ids = []
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Filter runs by created_at time range
        runs = [run['id'] for run in data['workflow_runs']
                    if START_TIME <= run['created_at'] <= END_TIME 
                    # and run['head_branch'] == 'main'
                ]
        all_run_ids.extend(runs)

        # Check for pagination
        url = None
        if 'next' in response.links:
            url = response.links['next']['url']
            print("retrieving from", url, "num runs: ", len(all_run_ids))

    return all_run_ids

# Fetch all workflow runs for the specified workflow
url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/workflows/{WORKFLOW_ID}/runs"
headers = {"Authorization": f"token {TOKEN}"}

# Extract run IDs from the JSON response, filtering by the time range
run_ids = fetch_runs(url, headers)

# Check if any runs are found in the time range
if not run_ids:
    print("No runs found in the specified time range.")
    exit(1)

# Loop through each workflow run
for run_id in run_ids:
    print(f"Downloading artifacts from run {run_id}...")

    # Get artifacts for the current run
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/actions/runs/{run_id}/artifacts"
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for failed requests
    
    # Extract artifact URLs and names from the JSON response
    artifacts = response.json()["artifacts"]
    for artifact in artifacts:
        if "Test Results" in artifact["name"]:
            artifact_name = artifact["name"]
            artifact_url = artifact["archive_download_url"]

            # Download the artifact to the zips folder
            filename = f"{artifact_name}.zip"
            zip_path = os.path.join(DESTINATION_DIR_ZIPS, filename)
            response = requests.get(artifact_url, headers=headers)
            response.raise_for_status()  # Raise an exception for failed requests
            with open(zip_path, "wb") as f:
                f.write(response.content)

            # Create a folder for unzipped artifact
            # artifact_dir = os.path.join(DESTINATION_DIR_DATA, artifact_name)
            # os.makedirs(artifact_dir, exist_ok=True)

            # # Ensure the directory is writable
            # os.chmod(artifact_dir, 0o777)

            # # Unzip the artifact
            # with zipfile.ZipFile(zip_path, "r") as zip_ref:
            #     zip_ref.extractall(artifact_dir)

            # Load data to list
            # test_data.append(collect_test_data(report_dir="./temp"))
            
            # Delete the zip and extracted files after unzipping to prevent storage from filling up
            # os.remove(zip_path)
            # shutil.rmtree(artifact_dir)

print("All artifacts downloaded and extracted successfully.")