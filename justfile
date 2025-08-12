set shell := ['zsh', '-cu']

default:
  @just --list

# Install dependencies
@install:
  uv sync

# Install with dev dependencies
@install-dev:
  uv sync --extra dev

# Run tests
@test:
  uv run pytest

# Run tests with coverage
@test-cov:
  uv run pytest --cov=hooks --cov-report=term-missing

# Lint code
@lint:
  uv run ruff check src/ tests/

# Format code
@format:
  uv run ruff format src/ tests/

# Check formatting
@check-format:
  uv run ruff format --check src/ tests/

# Run all checks (lint + format check + tests)
@check: check-format lint test

# Build the package
@build:
  uv build

# Clean build artifacts
@clean:
  rm -rf dist/ build/ *.egg-info/
  find . -type d -name __pycache__ -exec rm -rf {} +
  find . -type f -name "*.pyc" -delete

# Run the hooks module
@run:
  uv run hooks

# Show project info
@info:
  @echo "Project: cchooks"
  @echo "Python: $(uv python list --only-installed | head -1)"
  @echo "Dependencies:"
  @uv tree

