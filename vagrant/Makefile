.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([0-9a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: start-all
start-all: ## start a cluster of vagrant machines
	vagrant up --no-provision infra0 infra1 infra2
	vagrant provision infra0 || true
	vagrant provision infra1
	vagrant up client

.PHONY: destroy-all
destroy-all: ## destroy all vagrant machines
	vagrant destroy -f

.PHONY: start-infra2
start-infra2: ## start the infra2 node
	vagrant up --provision infra2


