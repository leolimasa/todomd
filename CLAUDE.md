# TODOMD Development Guide

## Build and Test Commands
```bash
# Install dependencies
poetry install

# Run all tests
python -m unittest discover

# Run a specific test
python -m unittest tests.test_airtable.TestAirtable.test_get_tasks

# Type checking
mypy todomd tests
```

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local imports with blank lines between groups
- **Type Annotations**: Use typing module for all function signatures and return types
- **Docstrings**: Required for all public functions with """triple quotes"""
- **Naming**: snake_case for variables/functions, PascalCase for classes, ALL_CAPS for constants
- **Error Handling**: Use try/except with specific exceptions, avoid bare except
- **Classes**: Use dataclasses for data containers
- **Project Structure**: Modular architecture with datasources as separate modules