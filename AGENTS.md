# Agent Instructions for flex-energy-price-calculator

## Project Overview

This is a Python CLI tool that calculates flex energy prices of electricity suppliers based on their tariff models. It uses the EEX (European Energy Exchange) API to fetch stock prices and applies various tariff models.

## Build, Lint, and Test Commands

### Installation
```bash
poetry install
```

### Running the Application
```bash
# Calculate for single month
poetry run flep --start 2024-03 --model oekoflow1.0

# Calculate for date range
poetry run flep --start 2024-01 --end 2024-03 --model gogreenenergyflex

# List available models
poetry run flep --list

# Generate markdown report
poetry run flep --format markdown --output docs
```

### Linting
```bash
# Run flake8 linter
poetry run flake8

# Run black formatter check
poetry run black --check .

# Format code with black
poetry run black .
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run single test file
poetry run pytest tests/test_models.py

# Run single test function
poetry run pytest tests/test_models.py::test_model_registry

# Run tests matching pattern
poetry run pytest -k "registry"

# Run with verbose output
poetry run pytest -v
```

## Code Style Guidelines

### General
- Python 3.12+
- Line length: 120 characters (max)
- Indentation: 4 spaces for Python files
- Use type hints for function parameters and return types
- Enable ruff or flake8 linting in your editor

### Formatting
- This project uses **Black** with `skip-string-normalization = true`
- Run `poetry run black .` before committing
- Do not add trailing commas in multi-line constructs (due to Black config)

### Linting Rules (flake8)
The project ignores:
- `D10` - Missing docstrings (no docstring requirements)
- `E203` - Whitespace before ':' (not PEP8 compliant)
- `W503` - Line break before binary operator

### Import Conventions
- Standard library imports first
- Third-party imports second
- Local/relative imports third
- Use relative imports within the package (e.g., `from ..base import BaseModel`)
- Model modules are imported with noqa for F401 (unused imports) since they're registered via decorators:
  ```python
  import flex_energy_price_calculator.models.oekostrom  # noqa: F401
  ```

### Naming Conventions
- **Classes**: PascalCase (e.g., `BaseModel`, `OekoFlow10`)
- **Functions/variables**: snake_case (e.g., `get_eex_prices`, `close_price`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `QUERY_DATE_FORMAT`, `TAXES`)
- **Private members**: leading underscore (e.g., `_first_close_price`)
- **Dataclasses**: PascalCase with descriptive names (e.g., `ModelMetadata`)

### Type Hints
- Use modern union syntax: `str | None` instead of `Optional[str]`
- Use `list[str]` instead of `List[str]` for generics
- Include return type annotations on all functions

### Error Handling
- Use specific exception types when possible
- For API errors, use `response.raise_for_status()`
- Handle `StatisticsError` from `statistics.mean()` when no data is available
- Use Typer's `BadParameter` for CLI validation errors

### Model Registration Pattern
Models use a decorator pattern for registration:
```python
from ..registry import register

@register(
    "model_name",
    description="Model description",
    fees=9.26,
    date_range_type="full_month",
    option_root="E.ATBM",
    days=10,
)
class MyModel(BaseModel):
    # implementation
```

The decorator:
1. Stores the model class and metadata in a registry
2. Attaches `__registry_metadata__` to the class
3. Must be imported to register (use noqa: F401 imports in command/__init__.py)

### Project Structure
```
flex_energy_price_calculator/
├── __init__.py
├── command/
│   └── __init__.py          # CLI entry point using Typer
├── models/
│   ├── __init__.py
│   ├── registry.py          # Model registration decorator
│   ├── base/
│   │   └── __init__.py      # BaseModel abstract class
│   ├── oekostrom/
│   ├── gogreenenergy/
│   ├── noprovider/
│   └── fullmonth/           # Each model in its own subpackage
├── report.py                # Markdown report generation
└── hack/                    # Miscellaneous utilities
```

### API Interaction
- EEX API endpoint: `https://webservice-eex.gvsi.com/query/json/getChain/...`
- API headers from environment variables: `EEX_API_HEADER_KEY`, `EEX_API_HEADER_VALUE`
- Results are cached in `.cache/` directory as JSON files

### Cache Management
- Cache files follow pattern: `{option_root}_{on_date}_{expiration_date}.json`
- Use `delete_cache_file()` to invalidate cache when needed

### Git Conventions
- Commit message format: `type: description` (e.g., `docs: update daily energy price report`)
- Types: `feat`, `fix`, `docs`, `chore`, etc.
- GH Actions runs daily at 06:00 UTC to generate reports

## Editor Configuration
The project includes `.editorconfig` for consistent editor settings. Ensure your editor supports EditorConfig or replicate these settings:
- Python: 4 spaces indent, 120 char line length
- YAML: 2 spaces indent
- JSON: 4 spaces indent
- End-of-line: LF
- Final newline: required
- Trim trailing whitespace: yes
