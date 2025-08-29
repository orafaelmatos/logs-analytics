# Testing Guide for Log Analytics Application

This directory contains comprehensive tests for the Log Analytics application, covering all routes, models, schemas, and business logic.

## 🏗️ Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_main.py             # Main API endpoint tests
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
# Using pytest directly
pytest
# Ou 
python -m pytest

# Using coverage
coverage run -m pytest
# Ou
coverage html
```

## 📊 Test Coverage

The test suite provides comprehensive coverage for:

### API Endpoints (`test_main.py`)
- ✅ **Root endpoint** (`/`)
- ✅ **Create log** (`POST /logs/`)
- ✅ **Get task status** (`GET /tasks/{task_id}`)
- ✅ **Get logs by service** (`GET /logs/service/{service_name}`)
- ✅ **Get logs by level** (`GET /logs/level/{level_name}`)
- ✅ **Get metrics by service** (`GET /metrics/service/{service_name}`)
- ✅ **Get metrics by level** (`GET /metrics/level/{level_name}`)
- ✅ **Get alerts** (`GET /alerts/`)

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)
- **Test discovery**: `tests/` directory
- **Coverage reporting**: HTML, XML, and terminal output
- **Async support**: Automatic async mode detection
- **Markers**: Strict marker validation
- **Output**: Verbose output with short tracebacks

### Test Fixtures (`conftest.py`)
- **Database sessions**: In-memory SQLite for fast tests
- **Mock clients**: FastAPI test clients
- **Mock services**: Celery, database, and external services
- **Test data**: Sample log data and metrics
- **Async support**: Proper async test setup

## 🧪 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run specific test class
pytest tests/test_main.py::TestCreateLogEndpoint

# Run specific test method
pytest tests/test_main.py::TestCreateLogEndpoint::test_create_log_success
```

### Advanced Options

```bash
# Run tests matching pattern
pytest -k "create_log"

# Run tests with debugger on failure
pytest --pdb

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l
```

## 📈 Coverage Reports

After running tests with coverage, you'll get:

- **Terminal output**: Summary of coverage
- **HTML report**: `htmlcov/index.html` - Interactive coverage browser
- **XML report**: `coverage.xml` - For CI/CD integration

### Coverage Targets
- **Overall coverage**: Target 90%+
- **Critical paths**: Target 95%+
- **API endpoints**: Target 100%
- **Business logic**: Target 95%+

## 🐛 Debugging Tests

### Debug Mode
```bash
# Run with pytest debugger
pytest --pdb
```

### Common Issues

1. **Import errors**: Ensure you're in the correct directory
2. **Database errors**: Check test database configuration
3. **Async errors**: Verify async test setup
4. **Mock errors**: Check mock configurations

### Test Isolation
- Each test runs in isolation
- Database is reset between tests
- Mocks are reset automatically
- No shared state between tests

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### GitLab CI Example
```yaml
test:
  stage: test
  script:
    - pip install -r requirements-test.txt
    - python run_tests.py --coverage
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 📚 Best Practices

### Test Design
- **Arrange-Act-Assert**: Clear test structure
- **Descriptive names**: Test names explain what they test
- **Single responsibility**: Each test tests one thing
- **Independent**: Tests don't depend on each other

### Test Data
- **Fixtures**: Reusable test data
- **Factories**: Dynamic test data generation
- **Cleanup**: Proper test cleanup
- **Realistic data**: Use realistic test scenarios

### Mocking
- **External services**: Mock external dependencies
- **Database**: Use test database or mocks
- **Time**: Mock time-dependent operations
- **Random**: Mock random operations for consistency

### Performance
- **Fast execution**: Tests should run quickly
- **Efficient setup**: Minimize test setup time
- **Parallel execution**: Use parallel test execution
- **Resource cleanup**: Clean up resources properly

