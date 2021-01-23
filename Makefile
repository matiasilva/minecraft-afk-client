MODULE := minecraft-afk
BLUE='\033[0;34m'
NC='\033[0m' # No Color

run:
	@python3 -m $(MODULE)

test:
	@pytest

lint:
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8 $(MODULE)

clean:
	rm -rf .pytest_cache .pytest_cache

.PHONY: clean test