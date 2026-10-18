.PHONY: help install run lint format reset dump-rules dump-cell-format

# workaround for argv
# Extract the arguments from the command line goals
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
# Turn the parsed goals into do-nothing targets so make does not complain
$(eval $(RUN_ARGS):;@:)

# Set the default goal to 'help' when someone just types 'make'
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# TODO test
# TODO clean

run: ## Run main module with uv
	uv run theory-crafft

dump-rules: ## Fetch the list of current rules on the sheet and print them. Useful for getting color decimal since these functions don't take hex or integer RGS values
	uv run dump-rules

dump-cell-format: ## Fetch any formatting applied to the cell, useful for getting payload of text style (bold font), colors, and borders
	uv run dump-cell-format $(RUN_ARGS)

reset: ## Clear out all sheet values and conditional formatting rules
	uv run reset

clear-token: ## After a certain amount of time, the token will be invalidated by google and must be re-authorized. The gspread library doesn't handle this very gracefully so you have to delete the token file for a new one to be generated using your secret. Its buried in a hidden folder in home dir so this command is a convenience to avoid having to `ls` a bunch. Only works on posix systems
	rm ~/.config/gspread/authorized_user.json

lint: ## Run ruff to fix for errors, style violations, and unused imports
	uv run ruff check --fix

format: ## Run ruff format for Black PEP 8 compliant opinionated formatting
	uv run ruff format
