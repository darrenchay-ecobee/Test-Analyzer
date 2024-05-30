# Variables
VENV_DIR = venv
REQUIREMENTS = requirements.txt
NOTEBOOK = test_data_vizualizer.ipynb

# Targets
.PHONY: all setup run clean

# Include .env file
include .env

all: setup run

activate: setup
	source $(VENV_DIR)/bin/activate

# Gets all requirements and sets up repo to start using it
setup: $(REQUIREMENTS)
	python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && pip install -r $(REQUIREMENTS)
	touch $(VENV_DIR)/bin/activate

run-analyze: setup
	. $(VENV_DIR)/bin/activate && python3 analyze_tests.py

notebook: setup
	. $(VENV_DIR)/bin/activate && jupyter notebook $(NOTEBOOK)

download_tests:
	@source .env && ./download_tests_from_github.sh

clean:
	rm -rf $(VENV_DIR)


