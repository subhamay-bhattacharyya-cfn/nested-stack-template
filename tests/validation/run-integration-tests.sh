#!/bin/bash

# CloudFormation Template Integration Test Runner
# Executes comprehensive integration test scenarios for the S3 bucket template

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEMPLATE_PATH="cfn/template.yaml"
RESULTS_DIR="tests/validation/results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${BLUE}=== CloudFormation Template Integration Tests ===${NC}"
echo "Template: $TEMPLATE_PATH"
echo "Results Directory: $RESULTS_DIR"
echo "Timestamp: $TIMESTAMP"
echo

# Create results directory
mkdir -p "$RESULTS_DIR"

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local log_file="$RESULTS_DIR/${test_name}_${TIMESTAMP}.log"
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo "Command: $test_command"
    echo "Log: $log_file"
    
    if eval "$test_command" > "$log_file" 2>&1; then
        echo -e "${GREEN}✓ PASSED: $test_name${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED: $test_name${NC}"
        echo "Error details in: $log_file"
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check if template exists
    if [ ! -f "$TEMPLATE_PATH" ]; then
        echo -e "${RED}Error: Template file not found: $TEMPLATE_PATH${NC}"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is required${NC}"
        exit 1
    fi
    
    # Check required Python modules
    python3 -c "import yaml, boto3" 2>/dev/null || {
        echo -e "${YELLOW}Warning: Some Python modules may be missing (yaml, boto3)${NC}"
        echo "Installing required modules..."
        pip3 install pyyaml boto3 2>/dev/null || echo -e "${YELLOW}Could not install modules automatically${NC}"
    }
    
    # Check AWS CLI (optional)
    if command -v aws &> /dev/null; then
        echo -e "${GREEN}✓ AWS CLI available${NC}"
    else
        echo -e "${YELLOW}⚠ AWS CLI not available (some tests may be limited)${NC}"
    fi
    
    echo -e "${GREEN}✓ Prerequisites check completed${NC}"
    echo
}

# Function to run template syntax validation
run_syntax_validation() {
    echo -e "${BLUE}=== Template Syntax Validation ===${NC}"
    
    # YAML syntax validation
    run_test "yaml_syntax_validation" "python3 -c \"
import yaml
with open('$TEMPLATE_PATH', 'r') as f:
    yaml.safe_load(f)
print('YAML syntax validation: PASSED')
\""
    
    # CloudFormation template validation (if AWS CLI available)
    if command -v aws &> /dev/null; then
        run_test "cloudformation_validation" "aws cloudformation validate-template --template-body file://$TEMPLATE_PATH --no-cli-pager"
    else
        echo -e "${YELLOW}⚠ Skipping AWS CloudFormation validation (AWS CLI not available)${NC}"
    fi
    
    echo
}

# Function to run parameter validation tests
run_parameter_validation() {
    echo -e "${BLUE}=== Parameter Validation Tests ===${NC}"
    
    if [ -f "tests/validation/test-parameter-validation.py" ]; then
        run_test "parameter_validation" "python3 tests/validation/test-parameter-validation.py"
    else
        echo -e "${YELLOW}⚠ Parameter validation test not found${NC}"
    fi
    
    echo
}

# Function to run conditional logic tests
run_conditional_logic_tests() {
    echo -e "${BLUE}=== Conditional Logic Tests ===${NC}"
    
    if [ -f "tests/validation/test-conditional-logic.py" ]; then
        run_test "conditional_logic" "python3 tests/validation/test-conditional-logic.py"
    else
        echo -e "${YELLOW}⚠ Conditional logic test not found${NC}"
    fi
    
    echo
}

# Function to run template generation tests
run_template_generation_tests() {
    echo -e "${BLUE}=== Template Generation Tests ===${NC}"
    
    if [ -f "tests/validation/test-template-generation.py" ]; then
        run_test "template_generation" "python3 tests/validation/test-template-generation.py"
    else
        echo -e "${YELLOW}⚠ Template generation test not found${NC}"
    fi
    
    echo
}

# Function to run integration scenario tests
run_integration_scenarios() {
    echo -e "${BLUE}=== Integration Scenario Tests ===${NC}"
    
    if [ -f "tests/validation/test-integration-scenarios.py" ]; then
        # Run in dry-run mode by default
        run_test "integration_scenarios_dry_run" "python3 tests/validation/test-integration-scenarios.py"
        
        # If AWS credentials are available and --live flag is passed, run live tests
        if [ "$1" = "--live" ] && aws sts get-caller-identity &> /dev/null; then
            echo -e "${YELLOW}Running live integration tests (this may create AWS resources)${NC}"
            read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                run_test "integration_scenarios_live" "python3 tests/validation/test-integration-scenarios.py --live"
            else
                echo -e "${YELLOW}Skipping live integration tests${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Integration scenarios test not found${NC}"
    fi
    
    echo
}

# Function to run cfn-lint validation (if available)
run_cfn_lint() {
    echo -e "${BLUE}=== CFN-Lint Validation ===${NC}"
    
    if command -v cfn-lint &> /dev/null; then
        run_test "cfn_lint" "cfn-lint $TEMPLATE_PATH"
    else
        echo -e "${YELLOW}⚠ cfn-lint not available (install with: pip install cfn-lint)${NC}"
    fi
    
    echo
}

# Function to generate comprehensive test report
generate_test_report() {
    local report_file="$RESULTS_DIR/comprehensive_test_report_${TIMESTAMP}.txt"
    
    echo -e "${BLUE}=== Generating Comprehensive Test Report ===${NC}"
    
    {
        echo "CloudFormation Template Integration Test Report"
        echo "=============================================="
        echo "Template: $TEMPLATE_PATH"
        echo "Test Date: $(date)"
        echo "Test Duration: $((SECONDS / 60)) minutes $((SECONDS % 60)) seconds"
        echo
        
        echo "Test Summary:"
        echo "-------------"
        
        # Count log files to determine test results
        local total_tests=0
        local passed_tests=0
        
        for log_file in "$RESULTS_DIR"/*_${TIMESTAMP}.log; do
            if [ -f "$log_file" ]; then
                total_tests=$((total_tests + 1))
                if grep -q "PASSED\|✓\|All.*tests passed" "$log_file" 2>/dev/null; then
                    passed_tests=$((passed_tests + 1))
                fi
            fi
        done
        
        echo "Total Tests: $total_tests"
        echo "Passed: $passed_tests"
        echo "Failed: $((total_tests - passed_tests))"
        
        if [ $total_tests -gt 0 ]; then
            local success_rate=$((passed_tests * 100 / total_tests))
            echo "Success Rate: ${success_rate}%"
        fi
        
        echo
        echo "Detailed Results:"
        echo "-----------------"
        
        for log_file in "$RESULTS_DIR"/*_${TIMESTAMP}.log; do
            if [ -f "$log_file" ]; then
                local test_name=$(basename "$log_file" "_${TIMESTAMP}.log")
                echo
                echo "=== $test_name ==="
                cat "$log_file"
            fi
        done
        
        echo
        echo "Generated Files:"
        echo "----------------"
        ls -la "$RESULTS_DIR"/*_${TIMESTAMP}* 2>/dev/null || echo "No additional files generated"
        
    } > "$report_file"
    
    echo "Comprehensive test report saved to: $report_file"
    echo
}

# Function to cleanup old test results (optional)
cleanup_old_results() {
    if [ "$1" = "--cleanup" ]; then
        echo -e "${BLUE}=== Cleaning up old test results ===${NC}"
        find "$RESULTS_DIR" -name "*.log" -mtime +7 -delete 2>/dev/null || true
        find "$RESULTS_DIR" -name "*.txt" -mtime +7 -delete 2>/dev/null || true
        echo -e "${GREEN}✓ Cleanup completed${NC}"
        echo
    fi
}

# Main execution
main() {
    local start_time=$SECONDS
    
    # Parse command line arguments
    local live_mode=false
    local cleanup_mode=false
    
    for arg in "$@"; do
        case $arg in
            --live)
                live_mode=true
                ;;
            --cleanup)
                cleanup_mode=true
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --live     Run live AWS integration tests (requires AWS credentials)"
                echo "  --cleanup  Clean up old test results (older than 7 days)"
                echo "  --help     Show this help message"
                exit 0
                ;;
        esac
    done
    
    # Run cleanup if requested
    if [ "$cleanup_mode" = true ]; then
        cleanup_old_results --cleanup
    fi
    
    # Run all test suites
    check_prerequisites
    run_syntax_validation
    run_parameter_validation
    run_conditional_logic_tests
    run_template_generation_tests
    
    if [ "$live_mode" = true ]; then
        run_integration_scenarios --live
    else
        run_integration_scenarios
    fi
    
    run_cfn_lint
    
    # Generate comprehensive report
    generate_test_report
    
    # Final summary
    local end_time=$SECONDS
    local duration=$((end_time - start_time))
    
    echo -e "${BLUE}=== Test Execution Complete ===${NC}"
    echo "Total Duration: $((duration / 60)) minutes $((duration % 60)) seconds"
    echo "Results Directory: $RESULTS_DIR"
    echo
    
    # Check overall success
    local failed_tests=0
    for log_file in "$RESULTS_DIR"/*_${TIMESTAMP}.log; do
        if [ -f "$log_file" ] && ! grep -q "PASSED\|✓\|All.*tests passed" "$log_file" 2>/dev/null; then
            failed_tests=$((failed_tests + 1))
        fi
    done
    
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}🎉 All integration tests completed successfully!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Check the results directory for details.${NC}"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"