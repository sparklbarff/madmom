# Installing Development Dependencies

This document explains how to install development dependencies for madmom2025.

## Quick Start

```bash
# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install madmom in development mode with dev dependencies
pip install -e ".[dev]"
```

## What Gets Installed

The `[dev]` extra includes:
- `pytest>=7.0` - Testing framework
- `pytest-cov>=4.0` - Coverage reporting
- `ruff>=0.1.0` - Fast Python linter

## Running Tests

After installing dev dependencies:

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v

# Run with coverage
pytest tests/ --cov=madmom --cov-report=html
```

## Building Documentation

Documentation dependencies are in the `[docs]` extra:

```bash
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

## System Python Restrictions

If you're using Homebrew Python on macOS, you may see errors about system packages.
This is intentional (PEP 668) to protect your system Python installation.

**Solution:** Always use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CI/CD

The GitHub Actions workflow (`.github/workflows/test.yml`) automatically:
1. Checks out the repository with submodules
2. Sets up Python 3.12, 3.13, 3.14
3. Installs dependencies: `pip install -e ".[dev]"`
4. Verifies Cython compilation
5. Verifies model submodule loading
6. Runs the full test suite

