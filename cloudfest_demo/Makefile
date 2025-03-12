DEFAULT_GOAL:  init


.PHONY: init
init:
	@echo "Initialize environment..."
	@if [ -f .venv ]; then rm -rf .venv; fi;
	@echo "Create virtual environment .venv";
	@python3 -m venv .venv;
	@echo "Init done."
	@echo "IMPORTANT: Dont forget to run 'source .venv/bin/activate' to activate the local python environment!"
	@echo "Upgrade pip and install wheel"
	@.venv/bin/python -m pip install --upgrade pip wheel;
	@echo "DONE"
	@echo "Installing dependencies...";
	@.venv/bin/python -m pip install -r requirements.txt;
	@echo "Done.";
