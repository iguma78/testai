# Contributing to TestAI SDK

Thank you for your interest in contributing to TestAI SDK! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/teleprompt-sdk.git
   cd teleprompt-sdk
   ```
3. Create a virtual environment and install development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run the tests to ensure everything works:
   ```bash
   pytest
   ```
4. Format your code:
   ```bash
   black teleprompt_sdk tests
   isort teleprompt_sdk tests
   ```
5. Commit your changes:
   ```bash
   git commit -m "Add your meaningful commit message here"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Create a pull request on GitHub

## Code Style

We follow the [Black](https://black.readthedocs.io/en/stable/) code style. Please ensure your code is formatted with Black before submitting a pull request.

## Testing

All new features and bugfixes should include tests. We use pytest for testing.

## Documentation

Please update the documentation when adding or modifying features. Documentation is written in Markdown and located in the `docs/` directory.

## Versioning

We use [Semantic Versioning](https://semver.org/). Please update the version number in `teleprompt_sdk/__init__.py` according to these guidelines.

## Release Process

1. Update the version number in `teleprompt_sdk/__init__.py`
2. Update the changelog
3. Create a new release on GitHub
4. The CI/CD pipeline will automatically publish the package to PyPI

## Code of Conduct

Please be respectful and considerate of others when contributing to the project.
