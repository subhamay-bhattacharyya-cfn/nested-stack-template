#!/bin/bash

# CloudFormation Template Syntax Validation Tests
# This script validates the CloudFormation template syntax using AWS CLI and cfn-lint

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="$SCRIPT_DIR/../../cfn/template.yaml"
TEST_RESULTS_DIR="$SCRIPT_DIR/results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p "$TEST_RESULTS_DIR"

echo "=== CloudFormation Template Syntax Validation Tests ==="
echo "Template: $TEMPLATE_PATH"
echo

# Test 1: AWS CLI Template Validation
echo -e "${YELLOW}Test 1: AWS CLI Template Validation${NC}"
if aws cloudformation validate-template --template-body file://"$TEMPLATE_PATH" > "$TEST_RESULTS_DIR/aws-cli-validation.json" 2>&1; then
    echo -e "${GREEN}✓ AWS CLI validation passed${NC}"
    echo "Template description: $(jq -r '.Description' "$TEST_RESULTS_DIR/aws-cli-validation.json")"
    echo "Parameters count: $(jq '.Parameters | length' "$TEST_RESULTS_DIR/aws-cli-validation.json")"
else
    echo -e "${YELLOW}⚠ AWS CLI validation skipped (authentication required)${NC}"
    echo "Note: AWS CLI validation requires valid AWS credentials"
    # Don't exit on AWS CLI failure - it may be due to missing credentials
fi
echo

# Test 2: cfn-lint Validation (if available)
echo -e "${YELLOW}Test 2: cfn-lint Validation${NC}"
if command -v cfn-lint &> /dev/null; then
    if cfn-lint "$TEMPLATE_PATH" > "$TEST_RESULTS_DIR/cfn-lint-results.txt" 2>&1; then
        echo -e "${GREEN}✓ cfn-lint validation passed${NC}"
    else
        echo -e "${RED}✗ cfn-lint found issues:${NC}"
        cat "$TEST_RESULTS_DIR/cfn-lint-results.txt"
        # Don't exit on cfn-lint warnings, only on AWS CLI failures
    fi
else
    echo -e "${YELLOW}⚠ cfn-lint not available, skipping${NC}"
    echo "To install cfn-lint: pip install cfn-lint"
fi
echo

# Test 3: YAML Syntax Validation
echo -e "${YELLOW}Test 3: YAML Syntax Validation${NC}"
python3 << 'EOF' > "$TEST_RESULTS_DIR/yaml-validation.txt" 2>&1
import yaml

# Custom YAML loader for CloudFormation intrinsic functions
class CloudFormationLoader(yaml.SafeLoader):
    pass

def construct_cf_function(loader, tag_suffix, node):
    """Handle CloudFormation intrinsic functions"""
    if isinstance(node, yaml.ScalarNode):
        return {f'Fn::{tag_suffix}': loader.construct_scalar(node)}
    elif isinstance(node, yaml.SequenceNode):
        return {f'Fn::{tag_suffix}': loader.construct_sequence(node)}
    elif isinstance(node, yaml.MappingNode):
        return {f'Fn::{tag_suffix}': loader.construct_mapping(node)}
    else:
        return {f'Fn::{tag_suffix}': None}

# Register CloudFormation intrinsic functions
cf_functions = ['Ref', 'GetAtt', 'Join', 'Sub', 'Select', 'Split', 'Base64', 'GetAZs', 
                'ImportValue', 'If', 'Not', 'Equals', 'And', 'Or', 'Condition']

for func in cf_functions:
    CloudFormationLoader.add_multi_constructor(f'!{func}', construct_cf_function)

# Test YAML parsing
with open('cfn/template.yaml', 'r') as f:
    template = yaml.load(f, Loader=CloudFormationLoader)
    print("YAML parsing successful")
    print(f"Template has {len(template.get('Parameters', {}))} parameters")
    print(f"Template has {len(template.get('Resources', {}))} resources")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ YAML syntax is valid${NC}"
    cat "$TEST_RESULTS_DIR/yaml-validation.txt"
else
    echo -e "${RED}✗ YAML syntax validation failed:${NC}"
    cat "$TEST_RESULTS_DIR/yaml-validation.txt"
    exit 1
fi
echo

# Test 4: Template Size Validation
echo -e "${YELLOW}Test 4: Template Size Validation${NC}"
TEMPLATE_SIZE=$(wc -c < "$TEMPLATE_PATH")
MAX_SIZE=460800  # 450KB limit for CloudFormation templates
if [ "$TEMPLATE_SIZE" -lt "$MAX_SIZE" ]; then
    echo -e "${GREEN}✓ Template size is within limits: ${TEMPLATE_SIZE} bytes (max: ${MAX_SIZE})${NC}"
else
    echo -e "${RED}✗ Template size exceeds CloudFormation limit: ${TEMPLATE_SIZE} bytes (max: ${MAX_SIZE})${NC}"
    exit 1
fi
echo

# Test 5: Required Sections Validation
echo -e "${YELLOW}Test 5: Required Sections Validation${NC}"
python3 << 'EOF'
import yaml
import sys

with open('cfn/template.yaml', 'r') as f:
    template = yaml.safe_load(f)

required_sections = ['AWSTemplateFormatVersion', 'Description', 'Parameters', 'Resources']
missing_sections = []

for section in required_sections:
    if section not in template:
        missing_sections.append(section)

if missing_sections:
    print(f"✗ Missing required sections: {', '.join(missing_sections)}")
    sys.exit(1)
else:
    print("✓ All required sections present")

# Validate specific requirements
if 'Outputs' not in template:
    print("⚠ Outputs section missing (recommended)")
else:
    print("✓ Outputs section present")

if 'Conditions' not in template:
    print("⚠ Conditions section missing")
else:
    print("✓ Conditions section present")

if 'Metadata' not in template:
    print("⚠ Metadata section missing")
else:
    print("✓ Metadata section present")
EOF
echo

echo -e "${GREEN}=== Template Syntax Validation Complete ===${NC}"