#!/bin/bash
# Same as test_download.py but in shell format
source .env

mkdir -p "$DESTINATION_DIR_ZIPS"
mkdir -p "$DESTINATION_DIR_DATA"

# Ensure the destination directory is writable
chmod +w "$DESTINATION_DIR_ZIPS"
chmod +w "$DESTINATION_DIR_DATA"

# Filter workflows by name and created_at time range
RUNS=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$OWNER/$REPO/actions/workflows/$WORKFLOW_ID/runs")

# Extract run IDs from the filtered JSON response
RUN_IDS=$(echo "$RUNS" | jq -r --arg START_TIME "$START_TIME" --arg END_TIME "$END_TIME" '.workflow_runs[] | select(.created_at >= $START_TIME and .created_at <= $END_TIME) | .id')
# echo "$RUN_IDS"

# Loop through each run
for RUN_ID in $RUN_IDS; do
    # Get artifacts for the current run
    ARTIFACTS=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/artifacts")

    # Extract artifact URLs and names from the JSON response
    ARTIFACTS_DATA=$(echo "$ARTIFACTS" | jq -r '.artifacts[] | select(.name | contains("Test Results")) | [.archive_download_url, .name] | @tsv')

    # Loop through each artifact URL and download it with the artifact name
    while IFS=$'\t' read -r ARTIFACT_URL ARTIFACT_NAME; do
        FILENAME="${ARTIFACT_NAME}.zip"
        echo "Downloading artifact $DESTINATION_DIR/$FILENAME..."
        curl -sL -o "$DESTINATION_DIR_ZIPS/$FILENAME" -H "Authorization: token $TOKEN" "$ARTIFACT_URL"

        # Create a folder for each artifact
        mkdir -p "$DESTINATION_DIR_DATA/$FILENAME"
        # Ensure the destination directory is writable
        chmod +w "$DESTINATION_DIR/$FILENAME"

        # Unzip the file after downloading
        echo "Unzipping artifact $FILENAME..."
        unzip -o "$DESTINATION_DIR_ZIPS/$FILENAME" -d "$DESTINATION_DIR_DATA/$FILENAME"
        
        # Delete the zip file after unzipping
        echo "Deleting artifact $FILENAME..."
        rm "$DESTINATION_DIR_ZIPS/$FILENAME"
    done <<< "$ARTIFACTS_DATA"
done