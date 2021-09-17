.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


.PHONY: lint
lint:  ## Linter the code.
	@echo "🚨 Linting code"
	poetry run isort basesqlmodel tests --check
	poetry run flake8 basesqlmodel tests
	poetry run mypy basesqlmodel
	poetry run black basesqlmodel tests --check --diff


.PHONY: format
format:
	@echo "🎨 Formatting code"
	poetry run isort basesqlmodel tests
	poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place basesqlmodel tests --exclude=__init__.py
	poetry run black basesqlmodel tests


.PHONY: test
test:  ## Test your code.
	@echo "🍜 Running pytest"
	poetry run pytest tests/ --cov=basesqlmodel --cov-report=term-missing:skip-covered --cov-report=xml --cov-fail-under 100
