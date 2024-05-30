# Test-Analyzer
This tool allows someone to retrieve java Jacoco test results which are uploaded as artifacts to GHA as an output of a workflow run.
There are 3 things in this repo: 
- a shell script to dowload the data and place it in a folder (both zipped and unzipped), as well as its python counterpart
- a python parser/analyzer which reads the downloaded data and saves it in csv format
- a jupyter notebook which uses logic from both of the previously mentionned items to download, parse, analyze, and visualize the data in a somewhat efficient way (still a lot of room for improvement)
  - **NOTE:** this is the most up to date code, and if the other python scripts aren't working, you should be able to copy and paste whats in this file and it _should_ work

## Setup
- Make sure you have python3 installed
- Run the `make setup` command from the makefile to download all python requirements and setup the VENV directory 
- to view and run the jupyter notebook, you can setup the jupyter notebook extension for vscode 
  - The main thing to do for setup is ensuring you have the correct kernel chosen (the VENV which should have been activated from running `make setup`)
- Create a .env file (there is the `.sample.env` available for the template) and update the variables there to the appropriate variables
- Create the folder which will hold the downloaded data temporarily

## How it works

### Downloading the data
- To retrieve the data, we parse the correct workflow to retrieve all the runs from GHA using its api
- Then, all the run ids are used to query for all the artifacts for that run
- Those artifacts (which are zipped) are then downloaded to the temporary folder `./<temp_folder_name>/zips/`
- The artifacts are then unzipped to the `/data` folder within that temporary folder 
  - Each artifact is unzipped to a folder a unique name to prevent overwriting, since the tests would have the same names

### Parsing & Analyzing the data
- Once the data is unzipped, we parse over all the xml files for 1 run and save the test result data in a list which is then saved in a pandas dataframe for analysis
- this is repeated for each run and appended to the list
  - this allows us to get some overall metrics such as total number of runs, number of failures, flakeyness of a test, average time, etc
- The data is then manipulated and some relevant info is added as well (such as github link, classname)
- Some visualizations are then done with the data and is then saved to a csv file if needed
**Note:** Since there are a lot of files that are downloaded based off the time range, to prevent the storage from filling up, once we parse the data for one run, the folders are then deleted

