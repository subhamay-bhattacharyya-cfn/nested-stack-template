#!/usr/bin/env python3

"""
CloudFormation Template Generation Tests
Tests that the template generates valid CloudFormation JSON/YAML with various parameter combinations
"""

import json
import yaml
import sys
import os
from typing import Dict, Any, List

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

class TemplateGenerationTester:
    def __init__(self, template_path: str):
        self.template_path = template_path
        with open(template_path, 'r') as f:
            self.template = yaml.load(f, Loader=CloudFormationLoader)
        self.test_results = []
        self.test_scenarios = []
    
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
    
    def create_test_scenarios(self):
        """Create various parameter combination scenarios for testing"""
        
        # Scenario 1: Minimal configuration
        minimal_config = {
            'ProjectName': 'test-project',
            'Environment': 'devl',
            'S3BucketBaseName': 'my-bucket'
        }
        
        # Scenario 2: Full KMS encryption enabled
        kms_config = {
            'ProjectName': 'secure-project',
            'Environment': 'prod',
            'S3BucketBaseName': 'secure-bucket',
            'KmsMasterKeyArn': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012',
            'BucketVersioningEnabled': 'true'
        }
        
        # Scenario 3: Full lifecycle configuration
        lifecycle_config = {
            'ProjectName': 'lifecycle-project',
            'Environment': 'test',
            'S3BucketBaseName': 'lifecycle-bucket',
            'S3LifecycleConfigurationEnabled': 'true',
            'TransitionToStandardIAEnabled': 'true',
            'TransitionToStandardIADays': 30,
            'TransitionToIntelligentTieringEnabled': 'true',
            'TransitionToIntelligentTieringDays': 60,
            'TransitionToOneZoneIAEnabled': 'true',
            'TransitionToOneZoneIADays': 90,
            'TransitionToGlacierIREnabled': 'true',
            'TransitionToGlacierIRDays': 120,
            'TransitionToGlacierEnabled': 'true',
            'TransitionToGlacierDays': 180,
            'TransitionToDeepArchiveEnabled': 'true',
            'TransitionToDeepArchiveDays': 365,
            'EnableExpiration': 'true',
            'ExpirationDays': 2555
        }
        
        # Scenario 4: Lambda notifications enabled
        notification_config = {
            'ProjectName': 'notify-project',
            'Environment': 'devl',
            'S3BucketBaseName': 'notify-bucket',
            'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:my-function',
            'NotificationEvents': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*'],
            'Prefix': 'uploads/',
            'Suffix': '.jpg'
        }
        
        # Scenario 5: Full security configuration
        security_config = {
            'ProjectName': 'secure-project',
            'Environment': 'prod',
            'S3BucketBaseName': 'secure-bucket',
            'S3VpcEndpointId': 'vpce-12345678',
            'IAMRoleBaseName': 'MyS3AccessRole',
            'WhitelistedUserId': 'AIDACKCEVSQ6C2EXAMPLE',
            'WhitelistedRoleId': 'AROACKCEVSQ6C2EXAMPLE'
        }
        
        # Scenario 6: GitHub integration
        github_config = {
            'ProjectName': 'github-project',
            'Environment': 'devl',
            'S3BucketBaseName': 'github-bucket',
            'GitHubOrg': 'my-org',
            'GitHubRepo': 'my-repo',
            'CiBuild': 'build-123'
        }
        
        # Scenario 7: Everything enabled (comprehensive test)
        comprehensive_config = {
            'ProjectName': 'comprehensive',
            'Environment': 'prod',
            'S3BucketBaseName': 'comprehensive',
            'GitHubOrg': 'my-org',
            'GitHubRepo': 'my-repo',
            'CiBuild': 'build-456',
            'KmsMasterKeyArn': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012',
            'BucketVersioningEnabled': 'true',
            'S3LifecycleConfigurationEnabled': 'true',
            'TransitionToStandardIAEnabled': 'true',
            'TransitionToStandardIADays': 30,
            'TransitionToGlacierEnabled': 'true',
            'TransitionToGlacierDays': 180,
            'EnableExpiration': 'true',
            'ExpirationDays': 2555,
            'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:processor',
            'S3VpcEndpointId': 'vpce-87654321',
            'IAMRoleBaseName': 'ComprehensiveRole'
        }
        
        self.test_scenarios = [
            ('Minimal Configuration', minimal_config),
            ('KMS Encryption Enabled', kms_config),
            ('Full Lifecycle Configuration', lifecycle_config),
            ('Lambda Notifications', notification_config),
            ('Security Configuration', security_config),
            ('GitHub Integration', github_config),
            ('Comprehensive Configuration', comprehensive_config)
        ]
    
    def validate_template_structure(self, scenario_name: str, template_dict: Dict[str, Any]):
        """Validate the basic structure of the generated template"""
        
        # Check required top-level sections
        required_sections = ['AWSTemplateFormatVersion', 'Description', 'Parameters', 'Resources']
        for section in required_sections:
            if section in template_dict:
                self.log_test(f"{scenario_name} - {section} section present", True)
            else:
                self.log_test(f"{scenario_name} - {section} section present", False, f"Missing {section}")
        
        # Check optional but expected sections
        optional_sections = ['Metadata', 'Conditions', 'Outputs']
        for section in optional_sections:
            if section in template_dict:
                self.log_test(f"{scenario_name} - {section} section present", True)
            else:
                self.log_test(f"{scenario_name} - {section} section present", False, f"Missing {section} (optional)")
    
    def validate_resources(self, scenario_name: str, template_dict: Dict[str, Any]):
        """Validate that required resources are present"""
        resources = template_dict.get('Resources', {})
        
        # Check for required resources
        required_resources = ['S3Bucket', 'S3BucketPolicy']
        for resource in required_resources:
            if resource in resources:
                self.log_test(f"{scenario_name} - {resource} resource present", True)
            else:
                self.log_test(f"{scenario_name} - {resource} resource present", False, f"Missing {resource}")
        
        # Validate S3 bucket resource structure
        s3_bucket = resources.get('S3Bucket', {})
        if s3_bucket:
            if 'Type' in s3_bucket and s3_bucket['Type'] == 'AWS::S3::Bucket':
                self.log_test(f"{scenario_name} - S3Bucket has correct type", True)
            else:
                self.log_test(f"{scenario_name} - S3Bucket has correct type", False, "Type should be AWS::S3::Bucket")
            
            if 'Properties' in s3_bucket:
                self.log_test(f"{scenario_name} - S3Bucket has Properties", True)
                
                properties = s3_bucket['Properties']
                if 'BucketName' in properties:
                    self.log_test(f"{scenario_name} - S3Bucket has BucketName", True)
                else:
                    self.log_test(f"{scenario_name} - S3Bucket has BucketName", False)
            else:
                self.log_test(f"{scenario_name} - S3Bucket has Properties", False)
    
    def validate_outputs(self, scenario_name: str, template_dict: Dict[str, Any]):
        """Validate template outputs"""
        outputs = template_dict.get('Outputs', {})
        
        if 'S3BucketArn' in outputs:
            self.log_test(f"{scenario_name} - S3BucketArn output present", True)
            
            output_def = outputs['S3BucketArn']
            if 'Description' in output_def:
                self.log_test(f"{scenario_name} - S3BucketArn has description", True)
            else:
                self.log_test(f"{scenario_name} - S3BucketArn has description", False)
            
            if 'Value' in output_def:
                self.log_test(f"{scenario_name} - S3BucketArn has value", True)
            else:
                self.log_test(f"{scenario_name} - S3BucketArn has value", False)
        else:
            self.log_test(f"{scenario_name} - S3BucketArn output present", False)
    
    def test_json_generation(self, scenario_name: str, parameters: Dict[str, Any]):
        """Test JSON generation for a scenario"""
        try:
            # Create a copy of the template with default parameter values
            template_copy = self.template.copy()
            
            # Apply parameter defaults
            if 'Parameters' in template_copy:
                for param_name, param_def in template_copy['Parameters'].items():
                    if param_name in parameters:
                        # Set the parameter value (in real CloudFormation, this would be done during deployment)
                        param_def['Default'] = parameters[param_name]
            
            # Convert to JSON
            json_output = json.dumps(template_copy, indent=2, default=str)
            
            # Validate JSON syntax
            json.loads(json_output)
            self.log_test(f"{scenario_name} - JSON generation", True, f"Generated {len(json_output)} characters")
            
            # Save JSON for inspection
            os.makedirs('tests/validation/results', exist_ok=True)
            json_filename = f"tests/validation/results/{scenario_name.lower().replace(' ', '_')}.json"
            with open(json_filename, 'w') as f:
                f.write(json_output)
            
            return json.loads(json_output)
            
        except Exception as e:
            self.log_test(f"{scenario_name} - JSON generation", False, f"Error: {str(e)}")
            return None
    
    def test_yaml_generation(self, scenario_name: str, parameters: Dict[str, Any]):
        """Test YAML generation for a scenario"""
        try:
            # Create a copy of the template with parameter values
            template_copy = self.template.copy()
            
            # Apply parameter defaults
            if 'Parameters' in template_copy:
                for param_name, param_def in template_copy['Parameters'].items():
                    if param_name in parameters:
                        param_def['Default'] = parameters[param_name]
            
            # Convert to YAML
            yaml_output = yaml.dump(template_copy, default_flow_style=False, sort_keys=False)
            
            # Validate YAML syntax
            yaml.safe_load(yaml_output)
            self.log_test(f"{scenario_name} - YAML generation", True, f"Generated {len(yaml_output)} characters")
            
            # Save YAML for inspection
            os.makedirs('tests/validation/results', exist_ok=True)
            yaml_filename = f"tests/validation/results/{scenario_name.lower().replace(' ', '_')}.yaml"
            with open(yaml_filename, 'w') as f:
                f.write(yaml_output)
            
            return yaml.safe_load(yaml_output)
            
        except Exception as e:
            self.log_test(f"{scenario_name} - YAML generation", False, f"Error: {str(e)}")
            return None
    
    def test_template_size_limits(self, scenario_name: str, template_dict: Dict[str, Any]):
        """Test that generated templates are within CloudFormation size limits"""
        if template_dict:
            # Test JSON size
            json_size = len(json.dumps(template_dict, default=str))
            max_size = 460800  # 450KB limit for CloudFormation templates
            
            if json_size < max_size:
                self.log_test(f"{scenario_name} - template size within limits", True, f"{json_size} bytes (max: {max_size})")
            else:
                self.log_test(f"{scenario_name} - template size within limits", False, f"{json_size} bytes exceeds limit of {max_size}")
    
    def test_parameter_references(self, scenario_name: str, template_dict: Dict[str, Any], parameters: Dict[str, Any]):
        """Test that all provided parameters are referenced in the template"""
        template_str = json.dumps(template_dict, default=str)
        
        for param_name in parameters.keys():
            if param_name in template_str:
                self.log_test(f"{scenario_name} - parameter '{param_name}' is referenced", True)
            else:
                self.log_test(f"{scenario_name} - parameter '{param_name}' is referenced", False, f"Parameter {param_name} not found in template")
    
    def run_scenario_tests(self, scenario_name: str, parameters: Dict[str, Any]):
        """Run all tests for a specific scenario"""
        print(f"\n=== Testing Scenario: {scenario_name} ===")
        
        # Test JSON generation
        json_template = self.test_json_generation(scenario_name, parameters)
        if json_template:
            self.validate_template_structure(scenario_name, json_template)
            self.validate_resources(scenario_name, json_template)
            self.validate_outputs(scenario_name, json_template)
            self.test_template_size_limits(scenario_name, json_template)
            self.test_parameter_references(scenario_name, json_template, parameters)
        
        # Test YAML generation
        yaml_template = self.test_yaml_generation(scenario_name, parameters)
        if yaml_template and json_template:
            # Compare JSON and YAML outputs for consistency
            try:
                # Normalize both for comparison (remove formatting differences)
                json_normalized = json.dumps(json_template, sort_keys=True, default=str)
                yaml_normalized = json.dumps(yaml_template, sort_keys=True, default=str)
                
                if json_normalized == yaml_normalized:
                    self.log_test(f"{scenario_name} - JSON/YAML consistency", True)
                else:
                    self.log_test(f"{scenario_name} - JSON/YAML consistency", False, "JSON and YAML outputs differ")
            except Exception as e:
                self.log_test(f"{scenario_name} - JSON/YAML consistency", False, f"Comparison error: {str(e)}")
    
    def run_all_tests(self):
        """Run all template generation tests"""
        print("=== CloudFormation Template Generation Tests ===")
        print(f"Template: {self.template_path}")
        
        self.create_test_scenarios()
        print(f"Testing {len(self.test_scenarios)} scenarios")
        
        for scenario_name, parameters in self.test_scenarios:
            self.run_scenario_tests(scenario_name, parameters)
        
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
            print("All template generation tests passed!")
            return True

if __name__ == "__main__":
    tester = TemplateGenerationTester("cfn/template.yaml")
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)