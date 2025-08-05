#!/usr/bin/env python3

"""
CloudFormation Template Parameter Validation Tests
Tests parameter constraints, edge cases, and invalid inputs
"""

import json
import yaml
import re
import sys
from typing import Dict, Any, List, Tuple

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

class ParameterValidationTester:
    def __init__(self, template_path: str):
        self.template_path = template_path
        with open(template_path, 'r') as f:
            self.template = yaml.load(f, Loader=CloudFormationLoader)
        self.parameters = self.template.get('Parameters', {})
        self.test_results = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
    
    def validate_pattern(self, param_name: str, pattern: str, test_values: List[Tuple[str, bool]]):
        """Validate parameter pattern constraints"""
        compiled_pattern = re.compile(pattern)
        
        for value, should_pass in test_values:
            matches = bool(compiled_pattern.match(value))
            test_name = f"{param_name} pattern validation: '{value}'"
            
            if matches == should_pass:
                self.log_test(test_name, True)
            else:
                expected = "should match" if should_pass else "should not match"
                self.log_test(test_name, False, f"Value '{value}' {expected} pattern '{pattern}'")
    
    def validate_length_constraints(self, param_name: str, min_length: int, max_length: int, test_values: List[Tuple[str, bool]]):
        """Validate parameter length constraints"""
        for value, should_pass in test_values:
            length = len(value)
            valid_length = min_length <= length <= max_length
            test_name = f"{param_name} length validation: '{value}' (length: {length})"
            
            if valid_length == should_pass:
                self.log_test(test_name, True)
            else:
                expected = f"should be between {min_length}-{max_length}" if should_pass else f"should not be between {min_length}-{max_length}"
                self.log_test(test_name, False, f"Length {length} {expected}")
    
    def validate_numeric_constraints(self, param_name: str, min_value: int, max_value: int, test_values: List[Tuple[int, bool]]):
        """Validate numeric parameter constraints"""
        for value, should_pass in test_values:
            valid_range = min_value <= value <= max_value
            test_name = f"{param_name} numeric validation: {value}"
            
            if valid_range == should_pass:
                self.log_test(test_name, True)
            else:
                expected = f"should be between {min_value}-{max_value}" if should_pass else f"should not be between {min_value}-{max_value}"
                self.log_test(test_name, False, f"Value {value} {expected}")
    
    def validate_allowed_values(self, param_name: str, allowed_values: List[str], test_values: List[Tuple[str, bool]]):
        """Validate allowed values constraints"""
        for value, should_pass in test_values:
            is_allowed = value in allowed_values
            test_name = f"{param_name} allowed values validation: '{value}'"
            
            if is_allowed == should_pass:
                self.log_test(test_name, True)
            else:
                expected = f"should be in {allowed_values}" if should_pass else f"should not be in {allowed_values}"
                self.log_test(test_name, False, f"Value '{value}' {expected}")
    
    def test_project_name_parameter(self):
        """Test ProjectName parameter validation"""
        print("\n=== Testing ProjectName Parameter ===")
        param = self.parameters.get('ProjectName', {})
        pattern = param.get('AllowedPattern', '')
        min_length = param.get('MinLength', 0)
        max_length = param.get('MaxLength', 999)
        
        # Pattern tests
        test_values = [
            ('my-project', True),      # Valid: lowercase with hyphens
            ('test123', True),         # Valid: lowercase with numbers
            ('a-b-c-d', True),         # Valid: multiple hyphens
            ('MyProject', False),      # Invalid: uppercase
            ('my_project', False),     # Invalid: underscore
            ('my project', False),     # Invalid: space
            ('my.project', False),     # Invalid: dot
            ('', False),               # Invalid: empty
            ('a', False),              # Invalid: too short (less than 5)
            ('ab', False),             # Invalid: too short
            ('abc', False),            # Invalid: too short
            ('abcd', False),           # Invalid: too short
            ('abcde', True),           # Valid: minimum length
            ('a' * 30, True),          # Valid: maximum length
            ('a' * 31, False),         # Invalid: too long
        ]
        
        self.validate_pattern('ProjectName', pattern, test_values)
        self.validate_length_constraints('ProjectName', min_length, max_length, test_values)
    
    def test_environment_parameter(self):
        """Test Environment parameter validation"""
        print("\n=== Testing Environment Parameter ===")
        param = self.parameters.get('Environment', {})
        allowed_values = param.get('AllowedValues', [])
        
        test_values = [
            ('devl', True),      # Valid
            ('test', True),      # Valid
            ('prod', True),      # Valid
            ('dev', False),      # Invalid
            ('development', False),  # Invalid
            ('staging', False),  # Invalid
            ('production', False),   # Invalid
            ('PROD', False),     # Invalid: case sensitive
            ('', False),         # Invalid: empty
        ]
        
        self.validate_allowed_values('Environment', allowed_values, test_values)
    
    def test_kms_key_arn_parameter(self):
        """Test KmsMasterKeyArn parameter validation"""
        print("\n=== Testing KmsMasterKeyArn Parameter ===")
        param = self.parameters.get('KmsMasterKeyArn', {})
        pattern = param.get('AllowedPattern', '')
        
        test_values = [
            ('', True),  # Valid: empty string allowed
            ('arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012', True),  # Valid KMS ARN
            ('arn:aws:kms:eu-west-1:987654321098:key/abcdef12-3456-7890-abcd-ef1234567890', True),  # Valid KMS ARN
            ('arn:aws-us-gov:kms:us-gov-west-1:123456789012:key/12345678-1234-1234-1234-123456789012', True),  # Valid GovCloud ARN
            ('invalid-arn', False),  # Invalid: not an ARN
            ('arn:aws:s3:::my-bucket', False),  # Invalid: S3 ARN instead of KMS
            ('arn:aws:kms:us-east-1:123456789012:alias/my-key', False),  # Invalid: alias instead of key
            ('arn:aws:kms:us-east-1:123456789012:key/invalid-key-id', False),  # Invalid: malformed key ID
        ]
        
        self.validate_pattern('KmsMasterKeyArn', pattern, test_values)
    
    def test_s3_bucket_base_name_parameter(self):
        """Test S3BucketBaseName parameter validation"""
        print("\n=== Testing S3BucketBaseName Parameter ===")
        param = self.parameters.get('S3BucketBaseName', {})
        pattern = param.get('AllowedPattern', '')
        min_length = param.get('MinLength', 0)
        max_length = param.get('MaxLength', 999)
        
        test_values = [
            ('my-bucket', True),       # Valid: lowercase with hyphens
            ('bucket123', True),       # Valid: lowercase with numbers
            ('my.bucket', True),       # Valid: dots allowed
            ('a-b-c', True),          # Valid: multiple hyphens
            ('abc', True),            # Valid: minimum length
            ('a' * 20, True),         # Valid: maximum length
            ('MyBucket', False),      # Invalid: uppercase
            ('my_bucket', False),     # Invalid: underscore
            ('my bucket', False),     # Invalid: space
            ('ab', False),            # Invalid: too short
            ('a' * 21, False),        # Invalid: too long
            ('', False),              # Invalid: empty
            ('-bucket', False),       # Invalid: starts with hyphen
            ('bucket-', False),       # Invalid: ends with hyphen
            ('.bucket', False),       # Invalid: starts with dot
            ('bucket.', False),       # Invalid: ends with dot
        ]
        
        self.validate_pattern('S3BucketBaseName', pattern, test_values)
        self.validate_length_constraints('S3BucketBaseName', min_length, max_length, test_values)
    
    def test_lifecycle_numeric_parameters(self):
        """Test lifecycle configuration numeric parameters"""
        print("\n=== Testing Lifecycle Numeric Parameters ===")
        
        # Test Standard-IA transition days
        param = self.parameters.get('TransitionToStandardIADays', {})
        min_val = param.get('MinValue', 0)
        max_val = param.get('MaxValue', 999)
        
        test_values = [
            (30, True),    # Valid: minimum
            (185, True),   # Valid: maximum
            (90, True),    # Valid: middle range
            (29, False),   # Invalid: below minimum
            (186, False),  # Invalid: above maximum
            (0, False),    # Invalid: zero
            (-1, False),   # Invalid: negative
        ]
        
        self.validate_numeric_constraints('TransitionToStandardIADays', min_val, max_val, test_values)
        
        # Test Deep Archive transition days
        param = self.parameters.get('TransitionToDeepArchiveDays', {})
        min_val = param.get('MinValue', 0)
        max_val = param.get('MaxValue', 999)
        
        test_values = [
            (365, True),   # Valid: minimum
            (500, True),   # Valid: maximum
            (400, True),   # Valid: middle range
            (364, False),  # Invalid: below minimum
            (501, False),  # Invalid: above maximum
        ]
        
        self.validate_numeric_constraints('TransitionToDeepArchiveDays', min_val, max_val, test_values)
    
    def test_lambda_function_arn_parameter(self):
        """Test LambdaFunctionArn parameter validation"""
        print("\n=== Testing LambdaFunctionArn Parameter ===")
        param = self.parameters.get('LambdaFunctionArn', {})
        pattern = param.get('AllowedPattern', '')
        
        test_values = [
            ('', True),  # Valid: empty string allowed
            ('arn:aws:lambda:us-east-1:123456789012:function:my-function', True),  # Valid Lambda ARN
            ('arn:aws:lambda:us-east-1:123456789012:function:my-function:$LATEST', True),  # Valid with version
            ('arn:aws:lambda:us-east-1:123456789012:function:my-function:1', True),  # Valid with version number
            ('arn:aws:lambda:us-east-1:123456789012:function:my-function:PROD', True),  # Valid with alias
            ('invalid-arn', False),  # Invalid: not an ARN
            ('arn:aws:s3:::my-bucket', False),  # Invalid: S3 ARN instead of Lambda
            ('arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1', False),  # Invalid: layer instead of function
        ]
        
        self.validate_pattern('LambdaFunctionArn', pattern, test_values)
    
    def test_vpc_endpoint_id_parameter(self):
        """Test S3VpcEndpointId parameter validation"""
        print("\n=== Testing S3VpcEndpointId Parameter ===")
        param = self.parameters.get('S3VpcEndpointId', {})
        pattern = param.get('AllowedPattern', '')
        
        test_values = [
            ('', True),  # Valid: empty string allowed
            ('vpce-12345678', True),  # Valid: 8 character ID
            ('vpce-1234567890abcdef1', True),  # Valid: 17 character ID
            ('vpce-abc123def456', True),  # Valid: mixed alphanumeric
            ('invalid-endpoint', False),  # Invalid: doesn't start with vpce-
            ('vpce-', False),  # Invalid: no ID after prefix
            ('vpce-1234567', False),  # Invalid: too short
            ('vpce-1234567890abcdef12', False),  # Invalid: too long
            ('VPCE-12345678', False),  # Invalid: uppercase
        ]
        
        self.validate_pattern('S3VpcEndpointId', pattern, test_values)
    
    def test_aws_user_id_parameters(self):
        """Test AWS User ID and Role ID parameters"""
        print("\n=== Testing AWS User/Role ID Parameters ===")
        
        # Test WhitelistedUserId
        param = self.parameters.get('WhitelistedUserId', {})
        pattern = param.get('AllowedPattern', '')
        
        test_values = [
            ('', True),  # Valid: empty string allowed
            ('AIDACKCEVSQ6C2EXAMPLE', True),  # Valid: 21 character user ID
            ('AROACKCEVSQ6C2EXAMPLE', True),  # Valid: 21 character role ID format
            ('AIDACKCEVSQ6C2EXAMPL', False),  # Invalid: 20 characters
            ('AIDACKCEVSQ6C2EXAMPLES', False),  # Invalid: 22 characters
            ('aidackcevsq6c2example', False),  # Invalid: lowercase
            ('AIDACKCEVSQ6C2EXAMPL!', False),  # Invalid: special character
        ]
        
        self.validate_pattern('WhitelistedUserId', pattern, test_values)
        
        # Test WhitelistedRoleId (same pattern)
        self.validate_pattern('WhitelistedRoleId', pattern, test_values)
    
    def test_github_parameters(self):
        """Test GitHub-related parameters"""
        print("\n=== Testing GitHub Parameters ===")
        
        # Test GitHubOrg
        param = self.parameters.get('GitHubOrg', {})
        pattern = param.get('AllowedPattern', '')
        max_length = param.get('MaxLength', 999)
        
        test_values = [
            ('', True),  # Valid: empty allowed
            ('my-org', True),  # Valid: lowercase with hyphens
            ('MyOrg123', True),  # Valid: mixed case with numbers
            ('a' * 50, True),  # Valid: maximum length
            ('a' * 51, False),  # Invalid: too long
            ('my_org', False),  # Invalid: underscore not allowed
            ('my org', False),  # Invalid: space not allowed
        ]
        
        self.validate_pattern('GitHubOrg', pattern, test_values[:7])  # Exclude length tests for pattern
        self.validate_length_constraints('GitHubOrg', 0, max_length, [(t[0], t[1]) for t in test_values if len(t[0]) <= 51])
    
    def run_all_tests(self):
        """Run all parameter validation tests"""
        print("=== CloudFormation Parameter Validation Tests ===")
        print(f"Template: {self.template_path}")
        print(f"Total parameters: {len(self.parameters)}")
        
        self.test_project_name_parameter()
        self.test_environment_parameter()
        self.test_kms_key_arn_parameter()
        self.test_s3_bucket_base_name_parameter()
        self.test_lifecycle_numeric_parameters()
        self.test_lambda_function_arn_parameter()
        self.test_vpc_endpoint_id_parameter()
        self.test_aws_user_id_parameters()
        self.test_github_parameters()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n=== Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\nFailed tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}")
                    if result['message']:
                        print(f"    {result['message']}")
            return False
        else:
            print("All parameter validation tests passed!")
            return True

if __name__ == "__main__":
    tester = ParameterValidationTester("cfn/template.yaml")
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)