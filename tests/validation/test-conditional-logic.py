#!/usr/bin/env python3

"""
CloudFormation Template Conditional Logic Tests
Tests various parameter combinations and conditional logic scenarios
"""

import json
import yaml
import sys
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

class ConditionalLogicTester:
    def __init__(self, template_path: str):
        self.template_path = template_path
        with open(template_path, 'r') as f:
            self.template = yaml.load(f, Loader=CloudFormationLoader)
        self.conditions = self.template.get('Conditions', {})
        self.parameters = self.template.get('Parameters', {})
        self.resources = self.template.get('Resources', {})
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
    
    def test_condition_definitions(self):
        """Test that all expected conditions are defined"""
        print("\n=== Testing Condition Definitions ===")
        
        expected_conditions = [
            'EnableKMSEncryption',
            'S3LifecycleConfigurationEnabled',
            'TransitionToStandardIAEnabled',
            'TransitionToIntelligentTieringEnabled',
            'TransitionToOneZoneIAEnabled',
            'TransitionToGlacierIREnabled',
            'TransitionToGlacierEnabled',
            'TransitionToDeepArchiveEnabled',
            'ExpirationEnabled',
            'BucketVersioningEnabled',
            'LambdaEventNotifyConfigEnabled',
            'HasNotificationPrefix',
            'HasNotificationSuffix',
            'HasNotificationFilters',
            'HasVpcEndpointRestriction',
            'HasWhitelistedUserId',
            'HasWhitelistedRoleId',
            'HasIAMRoleAccess'
        ]
        
        for condition in expected_conditions:
            if condition in self.conditions:
                self.log_test(f"Condition '{condition}' is defined", True)
            else:
                self.log_test(f"Condition '{condition}' is defined", False, f"Missing condition: {condition}")
    
    def test_kms_encryption_condition(self):
        """Test KMS encryption conditional logic"""
        print("\n=== Testing KMS Encryption Condition ===")
        
        # Test condition logic: EnableKMSEncryption should be true when KmsMasterKeyArn is not empty
        condition_def = self.conditions.get('EnableKMSEncryption')
        if condition_def:
            self.log_test("EnableKMSEncryption condition exists", True)
            
            # Check if condition uses !Not and !Equals with KmsMasterKeyArn
            condition_str = str(condition_def)
            if 'KmsMasterKeyArn' in condition_str and ('!Not' in condition_str or 'Fn::Not' in condition_str):
                self.log_test("EnableKMSEncryption uses correct logic", True, "Checks if KmsMasterKeyArn is not empty")
            else:
                self.log_test("EnableKMSEncryption uses correct logic", False, "Should check if KmsMasterKeyArn is not empty")
        else:
            self.log_test("EnableKMSEncryption condition exists", False)
    
    def test_lifecycle_conditions(self):
        """Test lifecycle configuration conditional logic"""
        print("\n=== Testing Lifecycle Conditions ===")
        
        # Test master lifecycle condition
        master_condition = self.conditions.get('S3LifecycleConfigurationEnabled')
        if master_condition:
            self.log_test("S3LifecycleConfigurationEnabled condition exists", True)
        else:
            self.log_test("S3LifecycleConfigurationEnabled condition exists", False)
        
        # Test individual storage class conditions
        storage_class_conditions = [
            'TransitionToStandardIAEnabled',
            'TransitionToIntelligentTieringEnabled',
            'TransitionToOneZoneIAEnabled',
            'TransitionToGlacierIREnabled',
            'TransitionToGlacierEnabled',
            'TransitionToDeepArchiveEnabled'
        ]
        
        for condition_name in storage_class_conditions:
            condition_def = self.conditions.get(condition_name)
            if condition_def:
                self.log_test(f"{condition_name} condition exists", True)
                
                # Check if condition uses !And with master lifecycle condition
                condition_str = str(condition_def)
                if ('!And' in condition_str or 'Fn::And' in condition_str) and 'S3LifecycleConfigurationEnabled' in condition_str:
                    self.log_test(f"{condition_name} uses correct logic", True, "Combines master condition with individual toggle")
                else:
                    self.log_test(f"{condition_name} uses correct logic", False, "Should combine master condition with individual toggle")
            else:
                self.log_test(f"{condition_name} condition exists", False)
    
    def test_notification_conditions(self):
        """Test notification conditional logic"""
        print("\n=== Testing Notification Conditions ===")
        
        # Test Lambda notification condition
        lambda_condition = self.conditions.get('LambdaEventNotifyConfigEnabled')
        if lambda_condition:
            self.log_test("LambdaEventNotifyConfigEnabled condition exists", True)
            
            condition_str = str(lambda_condition)
            if 'LambdaFunctionArn' in condition_str and ('!Not' in condition_str or 'Fn::Not' in condition_str):
                self.log_test("LambdaEventNotifyConfigEnabled uses correct logic", True, "Checks if LambdaFunctionArn is not empty")
            else:
                self.log_test("LambdaEventNotifyConfigEnabled uses correct logic", False, "Should check if LambdaFunctionArn is not empty")
        else:
            self.log_test("LambdaEventNotifyConfigEnabled condition exists", False)
        
        # Test notification filter conditions
        filter_conditions = ['HasNotificationPrefix', 'HasNotificationSuffix', 'HasNotificationFilters']
        for condition_name in filter_conditions:
            if condition_name in self.conditions:
                self.log_test(f"{condition_name} condition exists", True)
            else:
                self.log_test(f"{condition_name} condition exists", False)
    
    def test_security_conditions(self):
        """Test security-related conditional logic"""
        print("\n=== Testing Security Conditions ===")
        
        security_conditions = [
            'HasVpcEndpointRestriction',
            'HasWhitelistedUserId',
            'HasWhitelistedRoleId',
            'HasIAMRoleAccess'
        ]
        
        for condition_name in security_conditions:
            condition_def = self.conditions.get(condition_name)
            if condition_def:
                self.log_test(f"{condition_name} condition exists", True)
                
                # These should all check if their respective parameter is not empty
                condition_str = str(condition_def)
                if '!Not' in condition_str or 'Fn::Not' in condition_str:
                    self.log_test(f"{condition_name} uses correct logic", True, "Checks if parameter is not empty")
                else:
                    self.log_test(f"{condition_name} uses correct logic", False, "Should check if parameter is not empty")
            else:
                self.log_test(f"{condition_name} condition exists", False)
    
    def test_resource_conditional_properties(self):
        """Test that resources use conditions correctly"""
        print("\n=== Testing Resource Conditional Properties ===")
        
        # Test S3 bucket conditional properties
        s3_bucket = self.resources.get('S3Bucket', {})
        if s3_bucket:
            properties = s3_bucket.get('Properties', {})
            
            # Test BucketEncryption conditional property
            if 'BucketEncryption' in properties:
                encryption_config = properties['BucketEncryption']
                if isinstance(encryption_config, dict) and ('!If' in str(encryption_config) or 'Fn::If' in str(encryption_config)):
                    self.log_test("S3Bucket BucketEncryption uses conditional logic", True)
                else:
                    self.log_test("S3Bucket BucketEncryption uses conditional logic", False, "Should use !If with EnableKMSEncryption condition")
            else:
                self.log_test("S3Bucket BucketEncryption property exists", False)
            
            # Test LifecycleConfiguration conditional property
            if 'LifecycleConfiguration' in properties:
                lifecycle_config = properties['LifecycleConfiguration']
                if isinstance(lifecycle_config, dict) and ('!If' in str(lifecycle_config) or 'Fn::If' in str(lifecycle_config)):
                    self.log_test("S3Bucket LifecycleConfiguration uses conditional logic", True)
                else:
                    self.log_test("S3Bucket LifecycleConfiguration uses conditional logic", False, "Should use !If with S3LifecycleConfigurationEnabled condition")
            else:
                self.log_test("S3Bucket LifecycleConfiguration property exists", False)
            
            # Test NotificationConfiguration conditional property
            if 'NotificationConfiguration' in properties:
                notification_config = properties['NotificationConfiguration']
                if isinstance(notification_config, dict) and ('!If' in str(notification_config) or 'Fn::If' in str(notification_config)):
                    self.log_test("S3Bucket NotificationConfiguration uses conditional logic", True)
                else:
                    self.log_test("S3Bucket NotificationConfiguration uses conditional logic", False, "Should use !If with LambdaEventNotifyConfigEnabled condition")
            else:
                self.log_test("S3Bucket NotificationConfiguration property exists", False)
        else:
            self.log_test("S3Bucket resource exists", False)
    
    def test_bucket_policy_conditional_statements(self):
        """Test bucket policy conditional statements"""
        print("\n=== Testing Bucket Policy Conditional Statements ===")
        
        bucket_policy = self.resources.get('S3BucketPolicy', {})
        if bucket_policy:
            properties = bucket_policy.get('Properties', {})
            policy_document = properties.get('PolicyDocument', {})
            statements = policy_document.get('Statement', [])
            
            if statements:
                self.log_test("S3BucketPolicy has statements", True, f"Found {len(statements)} statements")
                
                # Check for conditional statements
                conditional_statements = 0
                for i, statement in enumerate(statements):
                    if isinstance(statement, dict) and ('!If' in str(statement) or 'Fn::If' in str(statement)):
                        conditional_statements += 1
                        self.log_test(f"Statement {i+1} uses conditional logic", True)
                
                if conditional_statements > 0:
                    self.log_test("Bucket policy has conditional statements", True, f"Found {conditional_statements} conditional statements")
                else:
                    self.log_test("Bucket policy has conditional statements", False, "No conditional statements found")
            else:
                self.log_test("S3BucketPolicy has statements", False)
        else:
            self.log_test("S3BucketPolicy resource exists", False)
    
    def test_parameter_combination_scenarios(self):
        """Test various parameter combination scenarios"""
        print("\n=== Testing Parameter Combination Scenarios ===")
        
        # Test scenario: All lifecycle transitions enabled
        scenario_name = "All lifecycle transitions enabled scenario"
        lifecycle_params = [
            'TransitionToStandardIAEnabled',
            'TransitionToIntelligentTieringEnabled',
            'TransitionToOneZoneIAEnabled',
            'TransitionToGlacierIREnabled',
            'TransitionToGlacierEnabled',
            'TransitionToDeepArchiveEnabled'
        ]
        
        all_lifecycle_conditions_exist = all(param.replace('Enabled', '') + 'Enabled' in self.conditions for param in lifecycle_params)
        self.log_test(f"{scenario_name} - all conditions exist", all_lifecycle_conditions_exist)
        
        # Test scenario: Security features enabled
        scenario_name = "Security features enabled scenario"
        security_params = [
            'HasVpcEndpointRestriction',
            'HasWhitelistedUserId',
            'HasWhitelistedRoleId',
            'HasIAMRoleAccess'
        ]
        
        all_security_conditions_exist = all(condition in self.conditions for condition in security_params)
        self.log_test(f"{scenario_name} - all conditions exist", all_security_conditions_exist)
        
        # Test scenario: Minimal configuration (no optional features)
        scenario_name = "Minimal configuration scenario"
        # In minimal scenario, most conditions should evaluate to false
        # This is tested by ensuring conditions exist and can handle empty/false values
        minimal_scenario_supported = True
        required_conditions = ['EnableKMSEncryption', 'S3LifecycleConfigurationEnabled', 'LambdaEventNotifyConfigEnabled']
        for condition in required_conditions:
            if condition not in self.conditions:
                minimal_scenario_supported = False
                break
        
        self.log_test(f"{scenario_name} - supported", minimal_scenario_supported)
    
    def test_condition_dependencies(self):
        """Test condition dependencies and hierarchies"""
        print("\n=== Testing Condition Dependencies ===")
        
        # Test that storage class conditions depend on master lifecycle condition
        storage_conditions = [
            'TransitionToStandardIAEnabled',
            'TransitionToIntelligentTieringEnabled',
            'TransitionToOneZoneIAEnabled',
            'TransitionToGlacierIREnabled',
            'TransitionToGlacierEnabled',
            'TransitionToDeepArchiveEnabled'
        ]
        
        for condition_name in storage_conditions:
            condition_def = self.conditions.get(condition_name)
            if condition_def:
                condition_str = str(condition_def)
                if 'S3LifecycleConfigurationEnabled' in condition_str:
                    self.log_test(f"{condition_name} depends on master lifecycle condition", True)
                else:
                    self.log_test(f"{condition_name} depends on master lifecycle condition", False, "Should reference S3LifecycleConfigurationEnabled")
            else:
                self.log_test(f"{condition_name} exists for dependency test", False)
        
        # Test that ExpirationEnabled depends on master lifecycle condition
        expiration_condition = self.conditions.get('ExpirationEnabled')
        if expiration_condition:
            condition_str = str(expiration_condition)
            if 'S3LifecycleConfigurationEnabled' in condition_str:
                self.log_test("ExpirationEnabled depends on master lifecycle condition", True)
            else:
                self.log_test("ExpirationEnabled depends on master lifecycle condition", False, "Should reference S3LifecycleConfigurationEnabled")
        else:
            self.log_test("ExpirationEnabled exists for dependency test", False)
    
    def run_all_tests(self):
        """Run all conditional logic tests"""
        print("=== CloudFormation Conditional Logic Tests ===")
        print(f"Template: {self.template_path}")
        print(f"Total conditions: {len(self.conditions)}")
        
        self.test_condition_definitions()
        self.test_kms_encryption_condition()
        self.test_lifecycle_conditions()
        self.test_notification_conditions()
        self.test_security_conditions()
        self.test_resource_conditional_properties()
        self.test_bucket_policy_conditional_statements()
        self.test_parameter_combination_scenarios()
        self.test_condition_dependencies()
        
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
            print("All conditional logic tests passed!")
            return True

if __name__ == "__main__":
    tester = ConditionalLogicTester("cfn/template.yaml")
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)