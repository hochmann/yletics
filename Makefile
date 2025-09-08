# Make Commands for Python Virtual Environment Setup

# .PHONY is used to declare phony targets, which are commands that don't produce a file with the same name.
.PHONY: all setup install clean

VENV_DIR = .venv
PYTHON_INTERPRETER = python3
REQUIREMENTS_FILE = requirements.txt

# `all` is the default target. It will run `setup` and then `install`.
all: setup install

# `setup` creates the virtual environment.
setup:
	@echo "Creating virtual environment..."
	$(PYTHON_INTERPRETER) -m venv $(VENV_DIR)

# `install` activates the virtual environment and installs the packages from the requirements file.
install:
	@echo "Installing dependencies..."
	@echo "Remember to run 'source .venv/bin/activate' to activate the environment."
	./$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

# `clean` removes the virtual environment directory.
clean:
	@echo "Cleaning up virtual environment..."
	rm -rf $(VENV_DIR)
