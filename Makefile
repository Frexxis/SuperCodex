.PHONY: install test test-plugin doctor verify lint format clean help

# Installation (local source, editable) - RECOMMENDED
install:
	@echo "🔧 Installing SuperCodex Framework (development mode)..."
	@uv venv
	@uv pip install -e ".[dev]"
	@echo ""
	@echo "✅ Installation complete!"
	@echo "   Run 'make verify' to check installation"

# Run tests
test:
	@echo "Running tests..."
	@uv run pytest

# Test pytest plugin loading
test-plugin:
	@echo "Testing pytest plugin auto-discovery..."
	@uv run python -m pytest --trace-config 2>&1 | grep -A2 "registered third-party plugins:" | grep supercodex && echo "✅ Plugin loaded successfully" || echo "❌ Plugin not loaded"

# Run doctor command
doctor:
	@echo "Running SuperCodex health check..."
	@uv run supercodex doctor

# Verify installation
verify:
	@echo "🔍 Installation Verification"
	@echo "======================================"
	@echo ""
	@echo "1. Package location:"
	@uv run python -c "import supercodex; print(f'   {supercodex.__file__}')"
	@echo ""
	@echo "2. Package version:"
	@uv run supercodex --version | sed 's/^/   /'
	@echo ""
	@echo "3. Pytest plugin:"
	@uv run python -m pytest --trace-config 2>&1 | grep "registered third-party plugins:" -A2 | grep supercodex | sed 's/^/   /' && echo "   ✅ Plugin loaded" || echo "   ❌ Plugin not loaded"
	@echo ""
	@echo "4. Health check:"
	@uv run supercodex doctor | grep "SuperCodex is healthy" > /dev/null && echo "   ✅ All checks passed" || echo "   ❌ Some checks failed"
	@echo ""
	@echo "======================================"
	@echo "✅ Verification complete"

# Linting
lint:
	@echo "Running linter..."
	@uv run ruff check .

# Format code
format:
	@echo "Formatting code..."
	@uv run ruff format .

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .pytest_cache -exec rm -rf {} +
	@find . -type d -name .ruff_cache -exec rm -rf {} +

# Show help
help:
	@echo "SuperCodex Framework - Available commands:"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make install         - Install in development mode (RECOMMENDED)"
	@echo "  make verify          - Verify installation is working"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make test            - Run test suite"
	@echo "  make test-plugin     - Test pytest plugin auto-discovery"
	@echo "  make doctor          - Run health check"
	@echo "  make lint            - Run linter (ruff check)"
	@echo "  make format          - Format code (ruff format)"
	@echo "  make clean           - Clean build artifacts"

