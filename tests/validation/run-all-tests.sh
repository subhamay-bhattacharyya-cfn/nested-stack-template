#!/bin/bash

# Master test runner for CloudFormation template validation
# Runs all validation tests and provides comprehensive reporting

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$RESULTS_DIR/test_report_$TIMESTAMP.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p "$RESULTS_DIR"

echo "=== CloudFormation Template Validation Test Suite ===" | tee "$REPORT_FILE"
echo "Started at: $(date)" | tee -a "$REPORT_FILE"
echo "Template: cfn/template.yaml" | tee -a "$REPORT_FILE"
echo | tee -a "$REPORT_FILE"

# Initialize counters
TOTAL_TEST_SUITES=0
PASSED_TEST_SUITES=0
FAILED_TEST_SUITES=0

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_file="$3"
    
    echo -e "${BLUE}=== Running $test_name ===${NC}" | tee -a "$REPORT_FILE"
    TOTAL_TEST_SUITES=$((TOTAL_TEST_SUITES + 1))
    
    if [ -f "$test_file" ]; then
        if eval "$test_command" >> "$REPORT_FILE" 2>&1; then
            echo -e "${GREEN}✓ $test_name PASSED${NC}" | tee -a "$REPORT_FILE"
            PASSED_TEST_SUITES=$((PASSED_TEST_SUITES + 1))
        else
            echo -e "${RED}✗ $test_name FAILED${NC}" | tee -a "$REPORT_FILE"
            FAILED_TEST_SUITES=$((FAILED_TEST_SUITES + 1))
        fi
    else
        echo -e "${RED}✗ $test_name FAILED - Test file not found: $test_file${NC}" | tee -a "$REPORT_FILE"
        FAILED_TEST_SUITES=$((FAILED_TEST_SUITES + 1))
    fi
    echo | tee -a "$REPORT_FILE"
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if AWS CLI is available
if command -v aws &> /dev/null; then
    echo "✓ AWS CLI is available"
else
    echo "⚠ AWS CLI not found - some tests may be skipped"
fi

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✓ Python 3 is available"
else
    echo "✗ Python 3 is required for validation tests"
    exit 1
fi

# Check if required Python modules are available
python3 -c "import yaml, json" 2>/dev/null && echo "✓ Required Python modules available" || {
    echo "✗ Required Python modules missing. Install with: pip install pyyaml"
    exit 1
}

# Check if cfn-lint is available
if command -v cfn-lint &> /dev/null; then
    echo "✓ cfn-lint is available"
else
    echo "⚠ cfn-lint not found - install with: pip install cfn-lint"
fi

echo

# Run test suites
echo -e "${BLUE}Starting test execution...${NC}" | tee -a "$REPORT_FILE"
echo

# Test 1: Template Syntax Validation
run_test "Template Syntax Validation" \
    "bash '$SCRIPT_DIR/test-template-syntax.sh'" \
    "$SCRIPT_DIR/test-template-syntax.sh"

# Test 2: Parameter Validation
run_test "Parameter Validation Tests" \
    "python3 '$SCRIPT_DIR/test-parameter-validation.py'" \
    "$SCRIPT_DIR/test-parameter-validation.py"

# Test 3: Conditional Logic Tests
run_test "Conditional Logic Tests" \
    "python3 '$SCRIPT_DIR/test-conditional-logic.py'" \
    "$SCRIPT_DIR/test-conditional-logic.py"

# Test 4: Template Generation Tests
run_test "Template Generation Tests" \
    "python3 '$SCRIPT_DIR/test-template-generation.py'" \
    "$SCRIPT_DIR/test-template-generation.py"

# Generate final report
echo "=== FINAL TEST REPORT ===" | tee -a "$REPORT_FILE"
echo "Completed at: $(date)" | tee -a "$REPORT_FILE"
echo | tee -a "$REPORT_FILE"
echo "Test Suite Summary:" | tee -a "$REPORT_FILE"
echo "  Total test suites: $TOTAL_TEST_SUITES" | tee -a "$REPORT_FILE"
echo "  Passed: $PASSED_TEST_SUITES" | tee -a "$REPORT_FILE"
echo "  Failed: $FAILED_TEST_SUITES" | tee -a "$REPORT_FILE"
echo | tee -a "$REPORT_FILE"

if [ $FAILED_TEST_SUITES -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Template validation successful.${NC}" | tee -a "$REPORT_FILE"
    echo | tee -a "$REPORT_FILE"
    echo "The CloudFormation template has passed all validation tests:" | tee -a "$REPORT_FILE"
    echo "  ✓ Template syntax is valid" | tee -a "$REPORT_FILE"
    echo "  ✓ Parameter constraints are properly defined" | tee -a "$REPORT_FILE"
    echo "  ✓ Conditional logic works correctly" | tee -a "$REPORT_FILE"
    echo "  ✓ Template generates valid CloudFormation JSON/YAML" | tee -a "$REPORT_FILE"
    echo | tee -a "$REPORT_FILE"
    echo "The template is ready for deployment and use as a nested stack." | tee -a "$REPORT_FILE"
    EXIT_CODE=0
else
    echo -e "${RED}❌ SOME TESTS FAILED! Please review the failures above.${NC}" | tee -a "$REPORT_FILE"
    echo | tee -a "$REPORT_FILE"
    echo "Failed test suites: $FAILED_TEST_SUITES out of $TOTAL_TEST_SUITES" | tee -a "$REPORT_FILE"
    echo "Please review the detailed output above and fix any issues." | tee -a "$REPORT_FILE"
    EXIT_CODE=1
fi

echo | tee -a "$REPORT_FILE"
echo "Detailed test report saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "Test artifacts saved in: $RESULTS_DIR" | tee -a "$REPORT_FILE"

# List generated files
echo | tee -a "$REPORT_FILE"
echo "Generated test artifacts:" | tee -a "$REPORT_FILE"
if [ -d "$RESULTS_DIR" ]; then
    ls -la "$RESULTS_DIR" | tee -a "$REPORT_FILE"
fi

exit $EXIT_CODE