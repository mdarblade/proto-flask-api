.PHONY: proto

proto-gen:
	@echo "Generating Protobuf files"
	@rm -rf py && mkdir py
	@rm -rf ruby && mkdir ruby
	@./scripts/protocgen.sh
	@echo Done
