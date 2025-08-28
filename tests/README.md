# Testing Guide for Log Analytics Application

This directory contains comprehensive tests for the Log Analytics application, covering all routes, models, schemas, and business logic.

## 🏗️ Test Structure

```
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_main.py             # Main API endpoint tests
├── test_schemas.py          # Pydantic schema validation tests
├── test_models.py           # SQLAlchemy model tests
├── test_database.py         # Database connection and utility tests
├── test_tasks.py            # Celery task tests
├── test_integration.py      # End-to-end integration tests
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Using pytest directly
python -m pytest

# Using the test runner script
python run_tests.py

# Using the test runner with coverage
python run_tests.py --coverage
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
python run_tests.py --unit

# API tests only
python run_tests.py --api

# Integration tests only
python run_tests.py --integration

# Database tests only
python run_tests.py --database

# Celery tests only
python run_tests.py --celery
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

### Schema Validation (`test_schemas.py`)
- ✅ **LogCreate schema** validation
- ✅ **Required field validation**
- ✅ **Data type validation**
- ✅ **Edge case handling**
- ✅ **Unicode and special character support**

### Database Models (`test_models.py`)
- ✅ **LogMetric model** CRUD operations
- ✅ **Database persistence**
- ✅ **Query operations**
- ✅ **Data integrity**
- ✅ **Performance considerations**

### Database Connections (`test_database.py`)
- ✅ **Async session management**
- ✅ **Connection pooling**
- ✅ **Error handling**
- ✅ **Transaction management**
- ✅ **MongoDB integration**

### Celery Tasks (`test_tasks.py`)
- ✅ **Task execution**
- ✅ **Database operations**
- ✅ **Error handling**
- ✅ **Data processing**
- ✅ **Return value validation**

### Integration Tests (`test_integration.py`)
- ✅ **End-to-end workflows**
- ✅ **Cross-component integration**
- ✅ **Data consistency**
- ✅ **Error propagation**
- ✅ **Performance under load**

## 🏷️ Test Markers

Tests are organized using pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.database` - Database-related tests
- `@pytest.mark.celery` - Celery task tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.asyncio` - Async tests

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
# Run tests in parallel
pytest -n auto

# Run tests matching pattern
pytest -k "create_log"

# Run tests with specific marker
pytest -m "api"

# Run tests with debugger on failure
pytest --pdb

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l
```

### Using the Test Runner Script

```bash
# Run all tests with coverage
python run_tests.py --coverage

# Run only unit tests
python run_tests.py --unit

# Run tests in parallel
python run_tests.py --parallel

# Run tests with verbose output
python run_tests.py --verbose

# Run tests matching pattern
python run_tests.py -k "create_log"

# Run tests with specific marker
python run_tests.py -m "api"
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
# Run with debug output
python run_tests.py --debug

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
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    python run_tests.py --coverage

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

## 🔍 Test Categories

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Single function, class, or method
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution

### Integration Tests
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Dependencies**: Real or mocked dependencies
- **Speed**: Medium execution time

### API Tests
- **Purpose**: Test HTTP endpoints
- **Scope**: Full request-response cycle
- **Dependencies**: Mocked backend services
- **Speed**: Fast execution

### End-to-End Tests
- **Purpose**: Test complete workflows
- **Scope**: Full system integration
- **Dependencies**: Real or test databases
- **Speed**: Slower execution

## 📝 Adding New Tests

### 1. Create Test File
```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    @pytest.mark.unit
    def test_new_feature_success(self):
        """Test successful new feature execution."""
        # Arrange
        # Act
        # Assert
        pass
```

### 2. Add Test Markers
```python
@pytest.mark.unit      # For unit tests
@pytest.mark.api       # For API tests
@pytest.mark.integration  # For integration tests
```

### 3. Use Fixtures
```python
def test_with_fixture(sample_log_data):
    """Test using fixture data."""
    assert sample_log_data["service"] == "test-service"
```

### 4. Mock Dependencies
```python
@patch('backend.app.database.AsyncSessionLocal')
def test_with_mock(mock_session):
    """Test with mocked dependency."""
    pass
```

## 🎯 Test Maintenance

### Regular Tasks
- **Update tests**: When features change
- **Review coverage**: Ensure adequate coverage
- **Performance**: Monitor test execution time
- **Dependencies**: Update test dependencies

### Quality Checks
- **Test isolation**: Ensure tests don't interfere
- **Mock usage**: Verify proper mocking
- **Error handling**: Test error scenarios
- **Edge cases**: Cover boundary conditions

## 📞 Support

For questions about the test suite:

1. **Check this README** for common solutions
2. **Review test examples** in existing test files
3. **Check pytest documentation** for advanced features
4. **Review coverage reports** for missing test areas

## 🎉 Success Metrics

- **Test coverage**: 90%+ overall
- **Test execution**: < 30 seconds for full suite
- **Test reliability**: 99%+ pass rate
- **Test maintenance**: Easy to add new tests
- **Developer experience**: Clear, helpful error messages
