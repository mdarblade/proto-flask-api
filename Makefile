.PHONY: help

APP_NAME=marketingmanager

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

proto-gen:
	@echo "Generating Protobuf files"
	@rm -rf protopython && mkdir protopython
	@rm -rf ruby && mkdir ruby
	@./scripts/protocgen.sh
	@echo Done

build: ## Build the container
	docker build -t $(APP_NAME) . --platform=linux/amd64   

run: ## Run container on port configured in `config.env`
	docker run -p 8080:8080 --rm $(APP_NAME) serve

deploy: ## Deploy to sagemaker
	@python scripts/deploy.py