# CloudFormation Template Validation Tests

This directory contains comprehensive validation tests for the S3 bucket CloudFormation template. The tests ensure template syntax correctness, parameter validation, conditional logic functionality, and proper template generation.

## Test Structure

### Test Files

1. **`test-template-syntax.sh`** - Template syntax validation using AWS CLI and cfn-lint
2. **`test-parameter-validation.py`** - Parameter constraint and validation testing
3. **`test-conditional-logic.py`** - Conditional logic and parameter combination testing
4. **`test-template-generation.py`** - Template generation and output validation
5. **`run-all-tests.sh`** - Master test runner that executes all validation tests

### Test Categories

#### 1. Template Syntax Validation
- AWS CLI template validation
- cfn-lint validation (if available)
- YAML syntax validation
- Template size validation
- Required sections validation

#### 2. Parameter Validation
- Pattern matching validation
- Length constraint validation
- Numeric range validation
- Allowed values validation
- Edge case testing

#### 3. Conditional Logic Testing
- Condition definition validation
- Condition dependency testing
- Resource conditional property testing
- Parameter combination scenarios
- Bucket policy conditional statements

#### 4. Template Generation Testing
- JSON generation validation
- YAML generation validation
- Multiple parameter scenarios
- Template structure validation
- Output validation

## Prerequisites

### Required Tools
- **AWS CLI** - For CloudFormation template validation
- **Python 3** - For running Python-based tests
- **PyYAML** - Python YAML library (`pip install pyyaml`)

### Optional Tools
- **cfn-lint** - Enhanced CloudFormation linting (`pip install cfn-lint`)

## Running Tests

### Run All Tests
```bash
# Make scripts executable
chmod +x tests/validation/*.sh

# Run complete test suite
./tests/validation/run-all-tests.sh
```

### Run Individual Test Suites

#### Template Syntax Tests
```bash
./tests/validation/test-template-syntax.sh
```

#### Parameter Validation Tests
```bash
python3 tests/validation/test-parameter-validation.py
```

#### Conditional Logic Tests
```bash
python3 tests/validation/test-conditional-logic.py
```

#### Template Generation Tests
```bash
python3 tests/validation/test-template-generation.py
```

## Test Scenarios

### Parameter Validation Scenarios
- **ProjectName**: Tests lowercase alphanumeric with hyphens, length constraints
- **Environment**: Tests allowed values (devl, test, prod)
- **KmsMasterKeyArn**: Tests ARN format validation and empty string handling
- **S3BucketBaseName**: Tests S3 bucket naming conventions
- **Lifecycle Parameters**: Tests numeric ranges for transition days
- **Lambda ARN**: Tests Lambda function ARN format validation
- **VPC Endpoint ID**: Tests VPC endpoint ID format validation
- **AWS User/Role IDs**: Tests 21-character AWS principal ID format

### Conditional Logic Scenarios
- **KMS Encryption**: Tests encryption enabling/disabling based on KMS key presence
- **Lifecycle Management**: Tests master toggle and individual storage class conditions
- **Event Notifications**: Tests Lambda notification conditional logic
- **Security Policies**: Tests VPC endpoint, user/role whitelisting conditions
- **Dependency Testing**: Tests condition hierarchies and dependencies

### Template Generation Scenarios
1. **Minimal Configuration** - Basic S3 bucket with required parameters only
2. **KMS Encryption Enabled** - Full encryption configuration
3. **Full Lifecycle Configuration** - All storage class transitions enabled
4. **Lambda Notifications** - Event notification configuration
5. **Security Configuration** - VPC endpoints and access restrictions
6. **GitHub Integration** - CI/CD integration parameters
7. **Comprehensive Configuration** - All features enabled

## Test Results

### Output Locations
- **Test Reports**: `tests/validation/results/test_report_YYYYMMDD_HHMMSS.txt`
- **Generated Templates**: `tests/validation/results/*.json` and `tests/validation/results/*.yaml`
- **Individual Test Results**: `tests/validation/results/`

### Success Criteria
All tests must pass for the template to be considered valid:
- ✅ Template syntax validation passes
- ✅ All parameter constraints work correctly
- ✅ Conditional logic functions as expected
- ✅ Template generates valid CloudFormation JSON/YAML
- ✅ All test scenarios produce valid templates

## Troubleshooting

### Common Issues

#### AWS CLI Not Available
```bash
# Install AWS CLI
pip install awscli
# or
brew install awscli  # macOS
```

#### Missing Python Dependencies
```bash
pip install pyyaml
```

#### cfn-lint Not Available
```bash
pip install cfn-lint
```

#### Permission Issues
```bash
chmod +x tests/validation/*.sh
```

### Test Failures

#### Parameter Validation Failures
- Check parameter patterns in template
- Verify constraint values match test expectations
- Review parameter descriptions and constraint messages

#### Conditional Logic Failures
- Verify condition definitions in template
- Check condition references in resources
- Ensure proper condition dependency chains

#### Template Generation Failures
- Check for YAML syntax errors
- Verify all required sections are present
- Review parameter default values

## Extending Tests

### Adding New Parameter Tests
1. Add test cases to `test-parameter-validation.py`
2. Include edge cases and boundary conditions
3. Test both valid and invalid inputs

### Adding New Conditional Logic Tests
1. Add condition tests to `test-conditional-logic.py`
2. Test condition combinations
3. Verify resource property conditional usage

### Adding New Generation Scenarios
1. Add scenarios to `test-template-generation.py`
2. Include parameter combinations
3. Test both minimal and comprehensive configurations

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: CloudFormation Template Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install pyyaml cfn-lint awscli
      - name: Run validation tests
        run: ./tests/validation/run-all-tests.sh
```

### Local Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit
./tests/validation/run-all-tests.sh
```

## Requirements Coverage

These tests fulfill the following requirements from the implementation plan:

- **Requirement 5.1**: Parameter validation with constraints and error messages
- **Requirement 5.3**: Comprehensive parameter validation for edge cases and invalid inputs
- Template syntax validation using AWS CLI and cfn-lint
- Conditional logic testing with various parameter combinations
- Template generation validation for CloudFormation JSON/YAML output

The test suite ensures the CloudFormation template is robust, well-validated, and ready for production deployment as a nested stack component.