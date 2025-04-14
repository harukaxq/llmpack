# Binary build Makefile for LLMPack

# Common variables
SRC_FILE = src/llmpack/cli.py
DEV_APP_NAME = dev_llmpack
PROD_APP_NAME = llmpack

# Development build settings
DEV_DIST_DIR = dist/dev
DEV_BUILD_DIR = build/dev
DEV_SPEC_FILE = $(DEV_APP_NAME).spec

# Production build settings
PROD_DIST_DIR = dist/prod
PROD_BUILD_DIR = build/prod
PROD_SPEC_FILE = $(PROD_APP_NAME).spec

.PHONY: all clean dev prod install fish-path upx-compress

# Default target
all: dev prod

# Install dependencies
install:
	uv add pyinstaller

# Development binary generation
dev:
	mkdir -p $(DEV_DIST_DIR)
	uv run pyinstaller --distpath=$(DEV_DIST_DIR) --workpath=$(DEV_BUILD_DIR) \
		--specpath=./spec --name=$(DEV_APP_NAME) \
		--hidden-import=pydantic --hidden-import=pydantic_core --hidden-import=pydantic.deprecated.decorator \
		--onefile $(SRC_FILE)

# Development binary generation (using existing spec file)
dev-spec: $(DEV_SPEC_FILE)
	uv run pyinstaller --distpath=$(DEV_DIST_DIR) --workpath=$(DEV_BUILD_DIR) ./spec/$(DEV_SPEC_FILE)

# Production binary generation
prod:
	mkdir -p $(PROD_DIST_DIR)
	uv run pyinstaller --distpath=$(PROD_DIST_DIR) --workpath=$(PROD_BUILD_DIR) \
		--specpath=./spec --name=$(PROD_APP_NAME) \
		--hidden-import=pydantic --hidden-import=pydantic_core --hidden-import=pydantic.deprecated.decorator \
		--onefile --clean $(SRC_FILE)

# Production binary generation (using existing spec file)
prod-spec: $(PROD_SPEC_FILE)
	uv run pyinstaller --distpath=$(PROD_DIST_DIR) --workpath=$(PROD_BUILD_DIR) ./spec/$(PROD_SPEC_FILE)

# Add to fish path (for development)
fish-path:
	@echo "Adding development binary to fish path..."
	@mkdir -p ~/.config/fish/conf.d
	@echo "# LLMPack development binary path" > ~/.config/fish/conf.d/llmpack.fish
	@echo "set -gx PATH $(PWD)/$(DEV_DIST_DIR) \$$PATH" >> ~/.config/fish/conf.d/llmpack.fish
	@echo "Fish path configuration created at ~/.config/fish/conf.d/llmpack.fish"
	@echo "Restart your fish shell or run 'source ~/.config/fish/conf.d/llmpack.fish' to apply changes"

# Cleanup
clean:
	rm -rf $(DEV_DIST_DIR) $(DEV_BUILD_DIR) $(PROD_DIST_DIR) $(PROD_BUILD_DIR)
	rm -f $(DEV_SPEC_FILE) $(PROD_SPEC_FILE)

# UPX compression for binaries
upx-compress:
	@command -v upx >/dev/null 2>&1 || { echo "UPX is not installed. Please install it first."; exit 1; }
	@echo "Compressing production binary with UPX..."
	@if [ -f "$(PROD_DIST_DIR)/$(PROD_APP_NAME)" ]; then \
		upx --best --lzma "$(PROD_DIST_DIR)/$(PROD_APP_NAME)"; \
		echo "Production binary compressed successfully."; \
	else \
		echo "Production binary not found. Run 'make prod' first."; \
	fi
	@echo "Compressing development binary with UPX..."
	@if [ -f "$(DEV_DIST_DIR)/$(DEV_APP_NAME)" ]; then \
		upx --best --lzma "$(DEV_DIST_DIR)/$(DEV_APP_NAME)"; \
		echo "Development binary compressed successfully."; \
	else \
		echo "Development binary not found. Run 'make dev' first."; \
	fi

# Help
help:
	@echo "Available targets:"
	@echo "  make dev        - Generate development binary (dev_llmpack)"
	@echo "  make prod       - Generate production binary (llmpack)"
	@echo "  make all        - Generate both development and production binaries"
	@echo "  make clean      - Remove generated files"
	@echo "  make install    - Install required dependencies"
	@echo "  make fish-path  - Add development binary to fish shell path"
	@echo "  make upx-compress - Compress binaries with UPX for smaller size"
	@echo "  make help       - Display this help message"
