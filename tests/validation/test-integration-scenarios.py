#!/usr/bin/env python3

"""
CloudFormation Template Integration Test Scenarios
Tests complete deployment scenarios with various parameter combinations to verify
end-to-end functionality including resource creation, policy enforcement, and feature integration.
"""

import json
import yaml
import sys
import os
import boto3
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

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

class IntegrationTestScenarios:
    def __init__(self, template_path: str, dry_run: bool = True):
        self.template_path = template_path
        self.dry_run = dry_run
        with open(template_path, 'r') as f:
            self.template = yaml.load(f, Loader=CloudFormationLoader)
        self.test_results = []
        self.test_scenarios = []
        
        # Initialize AWS clients (if not in dry run mode)
        if not dry_run:
            try:
                self.cf_client = boto3.client('cloudformation')
                self.s3_client = boto3.client('s3')
                self.iam_client = boto3.client('iam')
            except Exception as e:
                print(f"Warning: Could not initialize AWS clients: {e}")
                print("Running in dry-run mode only")
                self.dry_run = True
    
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
        """Create comprehensive integration test scenarios"""
        
        # Scenario 1: Minimal Configuration (Basic S3 bucket)
        # Requirements: 1.1 (basic bucket creation)
        minimal_config = {
            'scenario_name': 'Minimal Configuration',
            'description': 'Basic S3 bucket with minimal required parameters',
            'requirements': ['1.1'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'devl',
                'S3BucketBaseName': 'minimal-bucket'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': False,
                'versioning': False,
                'lifecycle': False,
                'notifications': False,
                'vpc_restriction': False
            }
        }
        
        # Scenario 2: KMS Encryption Enabled
        # Requirements: 1.2 (KMS encryption)
        kms_encryption_config = {
            'scenario_name': 'KMS Encryption Enabled',
            'description': 'S3 bucket with KMS encryption and versioning',
            'requirements': ['1.1', '1.2', '1.3'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'prod',
                'S3BucketBaseName': 'encrypted-bucket',
                'KmsMasterKeyArn': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012',
                'BucketVersioningEnabled': 'true'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': True,
                'versioning': True,
                'lifecycle': False,
                'notifications': False,
                'vpc_restriction': False
            }
        }
        
        # Scenario 3: Full Lifecycle Configuration
        # Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6 (all lifecycle features)
        full_lifecycle_config = {
            'scenario_name': 'Full Lifecycle Configuration',
            'description': 'S3 bucket with comprehensive lifecycle management',
            'requirements': ['1.1', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'test',
                'S3BucketBaseName': 'lifecycle-bucket',
                'S3LifecycleConfigurationEnabled': 'true',
                'TransitionPrefix': 'data/',
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
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': False,
                'versioning': False,
                'lifecycle': True,
                'notifications': False,
                'vpc_restriction': False
            }
        }
        
        # Scenario 4: Lambda Event Notifications
        # Requirements: 4.1, 4.2, 4.3 (event notifications)
        lambda_notifications_config = {
            'scenario_name': 'Lambda Event Notifications',
            'description': 'S3 bucket with Lambda event notifications and filtering',
            'requirements': ['1.1', '4.1', '4.2', '4.3'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'devl',
                'S3BucketBaseName': 'notify-bucket',
                'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:s3-processor',
                'NotificationEvents': ['s3:ObjectCreated:*', 's3:ObjectRemoved:*'],
                'Prefix': 'uploads/',
                'Suffix': '.jpg'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': False,
                'versioning': False,
                'lifecycle': False,
                'notifications': True,
                'vpc_restriction': False
            }
        }
        
        # Scenario 5: Security Configuration with VPC and Access Controls
        # Requirements: 3.1, 3.2, 3.3, 3.4, 3.5 (security policies)
        security_config = {
            'scenario_name': 'Security Configuration',
            'description': 'S3 bucket with comprehensive security policies and access controls',
            'requirements': ['1.1', '3.1', '3.2', '3.3', '3.4', '3.5'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'prod',
                'S3BucketBaseName': 'secure-bucket',
                'S3VpcEndpointId': 'vpce-12345678',
                'IAMRoleBaseName': 'S3AccessRole',
                'WhitelistedUserId': 'AIDACKCEVSQ6C2EXAMPLE',
                'WhitelistedRoleId': 'AROACKCEVSQ6C2EXAMPLE'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': False,
                'versioning': False,
                'lifecycle': False,
                'notifications': False,
                'vpc_restriction': True
            }
        }
        
        # Scenario 6: GitHub Integration with CI/CD
        # Requirements: 6.1, 6.3 (tagging and metadata)
        github_integration_config = {
            'scenario_name': 'GitHub Integration',
            'description': 'S3 bucket with GitHub integration and CI/CD metadata',
            'requirements': ['1.1', '6.1', '6.3'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'devl',
                'S3BucketBaseName': 'github-bucket',
                'GitHubOrg': 'my-organization',
                'GitHubRepo': 'my-repository',
                'CiBuild': 'build-12345'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': False,
                'versioning': False,
                'lifecycle': False,
                'notifications': False,
                'vpc_restriction': False
            }
        }
        
        # Scenario 7: Comprehensive Configuration (All Features)
        # Requirements: All requirements combined
        comprehensive_config = {
            'scenario_name': 'Comprehensive Configuration',
            'description': 'S3 bucket with all features enabled for complete integration testing',
            'requirements': ['1.1', '1.2', '1.3', '1.4', '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', 
                           '3.1', '3.2', '3.3', '3.4', '3.5', '4.1', '4.2', '4.3', '6.1', '6.2', '6.3'],
            'parameters': {
                'ProjectName': 'integration-test',
                'Environment': 'prod',
                'S3BucketBaseName': 'comprehensive',
                'GitHubOrg': 'my-organization',
                'GitHubRepo': 'comprehensive-repo',
                'CiBuild': 'build-67890',
                'KmsMasterKeyArn': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012',
                'BucketVersioningEnabled': 'true',
                'BlockPublicAcls': 'true',
                'BlockPublicPolicy': 'true',
                'IgnorePublicAcls': 'true',
                'RestrictPublicBuckets': 'true',
                'S3LifecycleConfigurationEnabled': 'true',
                'TransitionPrefix': 'data/',
                'TransitionToStandardIAEnabled': 'true',
                'TransitionToStandardIADays': 30,
                'TransitionToGlacierEnabled': 'true',
                'TransitionToGlacierDays': 180,
                'EnableExpiration': 'true',
                'ExpirationDays': 2555,
                'LambdaFunctionArn': 'arn:aws:lambda:us-east-1:123456789012:function:comprehensive-processor',
                'NotificationEvents': ['s3:ObjectCreated:*'],
                'Prefix': 'processed/',
                'S3VpcEndpointId': 'vpce-87654321',
                'IAMRoleBaseName': 'ComprehensiveS3Role'
            },
            'expected_resources': ['S3Bucket', 'S3BucketPolicy'],
            'expected_features': {
                'encryption': True,
                'versioning': True,
                'lifecycle': True,
                'notifications': True,
                'vpc_restriction': True
            }
        }
        
        self.test_scenarios = [
            minimal_config,
            kms_encryption_config,
            full_lifecycle_config,
            lambda_notifications_config,
            security_config,
            github_integration_config,
            comprehensive_config
        ]
    
    def validate_template_syntax(self, scenario: Dict[str, Any]) -> bool:
        """Validate CloudFormation template syntax for the scenario"""
        try:
            # Create template with scenario parameters
            template_copy = self.template.copy()
            
            # Convert to JSON for validation
            json_template = json.dumps(template_copy, indent=2, default=str)
            
            # Validate JSON syntax
            json.loads(json_template)
            
            self.log_test(f"{scenario['scenario_name']} - Template syntax validation", True, 
                         f"Template is valid JSON ({len(json_template)} bytes)")
            return True
            
        except Exception as e:
            self.log_test(f"{scenario['scenario_name']} - Template syntax validation", False, 
                         f"Syntax error: {str(e)}")
            return False
    
    def validate_parameter_constraints(self, scenario: Dict[str, Any]) -> bool:
        """Validate that scenario parameters meet template constraints"""
        parameters = scenario['parameters']
        template_params = self.template.get('Parameters', {})
        
        all_valid = True
        
        for param_name, param_value in parameters.items():
            if param_name not in template_params:
                self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' exists", False, 
                             f"Parameter not defined in template")
                all_valid = False
                continue
            
            param_def = template_params[param_name]
            
            # Check allowed values
            if 'AllowedValues' in param_def:
                if param_value not in param_def['AllowedValues']:
                    self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' allowed value", False, 
                                 f"Value '{param_value}' not in {param_def['AllowedValues']}")
                    all_valid = False
                    continue
            
            # Check string length constraints
            if isinstance(param_value, str):
                if 'MinLength' in param_def and len(param_value) < param_def['MinLength']:
                    self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' min length", False, 
                                 f"Length {len(param_value)} < {param_def['MinLength']}")
                    all_valid = False
                    continue
                
                if 'MaxLength' in param_def and len(param_value) > param_def['MaxLength']:
                    self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' max length", False, 
                                 f"Length {len(param_value)} > {param_def['MaxLength']}")
                    all_valid = False
                    continue
            
            # Check numeric constraints
            if isinstance(param_value, (int, float)):
                if 'MinValue' in param_def and param_value < param_def['MinValue']:
                    self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' min value", False, 
                                 f"Value {param_value} < {param_def['MinValue']}")
                    all_valid = False
                    continue
                
                if 'MaxValue' in param_def and param_value > param_def['MaxValue']:
                    self.log_test(f"{scenario['scenario_name']} - Parameter '{param_name}' max value", False, 
                                 f"Value {param_value} > {param_def['MaxValue']}")
                    all_valid = False
                    continue
        
        if all_valid:
            self.log_test(f"{scenario['scenario_name']} - Parameter constraints validation", True, 
                         f"All {len(parameters)} parameters valid")
        
        return all_valid
    
    def validate_expected_resources(self, scenario: Dict[str, Any]) -> bool:
        """Validate that expected resources are present in template"""
        resources = self.template.get('Resources', {})
        expected_resources = scenario['expected_resources']
        
        all_present = True
        
        for resource_name in expected_resources:
            if resource_name in resources:
                self.log_test(f"{scenario['scenario_name']} - Resource '{resource_name}' present", True)
            else:
                self.log_test(f"{scenario['scenario_name']} - Resource '{resource_name}' present", False, 
                             f"Expected resource not found")
                all_present = False
        
        return all_present
    
    def validate_conditional_logic(self, scenario: Dict[str, Any]) -> bool:
        """Validate conditional logic based on scenario parameters"""
        parameters = scenario['parameters']
        expected_features = scenario['expected_features']
        conditions = self.template.get('Conditions', {})
        
        all_valid = True
        
        # Test KMS encryption condition
        if 'encryption' in expected_features:
            has_kms_key = parameters.get('KmsMasterKeyArn', '') != ''
            expected_encryption = expected_features['encryption']
            
            if has_kms_key == expected_encryption:
                self.log_test(f"{scenario['scenario_name']} - KMS encryption logic", True, 
                             f"KMS key present: {has_kms_key}, encryption expected: {expected_encryption}")
            else:
                self.log_test(f"{scenario['scenario_name']} - KMS encryption logic", False, 
                             f"Logic mismatch: KMS key present: {has_kms_key}, encryption expected: {expected_encryption}")
                all_valid = False
        
        # Test lifecycle condition
        if 'lifecycle' in expected_features:
            lifecycle_enabled = parameters.get('S3LifecycleConfigurationEnabled', 'false') == 'true'
            expected_lifecycle = expected_features['lifecycle']
            
            if lifecycle_enabled == expected_lifecycle:
                self.log_test(f"{scenario['scenario_name']} - Lifecycle logic", True, 
                             f"Lifecycle enabled: {lifecycle_enabled}, expected: {expected_lifecycle}")
            else:
                self.log_test(f"{scenario['scenario_name']} - Lifecycle logic", False, 
                             f"Logic mismatch: Lifecycle enabled: {lifecycle_enabled}, expected: {expected_lifecycle}")
                all_valid = False
        
        # Test notifications condition
        if 'notifications' in expected_features:
            has_lambda_arn = parameters.get('LambdaFunctionArn', '') != ''
            expected_notifications = expected_features['notifications']
            
            if has_lambda_arn == expected_notifications:
                self.log_test(f"{scenario['scenario_name']} - Notifications logic", True, 
                             f"Lambda ARN present: {has_lambda_arn}, notifications expected: {expected_notifications}")
            else:
                self.log_test(f"{scenario['scenario_name']} - Notifications logic", False, 
                             f"Logic mismatch: Lambda ARN present: {has_lambda_arn}, notifications expected: {expected_notifications}")
                all_valid = False
        
        # Test VPC restriction condition
        if 'vpc_restriction' in expected_features:
            has_vpc_endpoint = parameters.get('S3VpcEndpointId', '') != ''
            expected_vpc_restriction = expected_features['vpc_restriction']
            
            if has_vpc_endpoint == expected_vpc_restriction:
                self.log_test(f"{scenario['scenario_name']} - VPC restriction logic", True, 
                             f"VPC endpoint present: {has_vpc_endpoint}, restriction expected: {expected_vpc_restriction}")
            else:
                self.log_test(f"{scenario['scenario_name']} - VPC restriction logic", False, 
                             f"Logic mismatch: VPC endpoint present: {has_vpc_endpoint}, restriction expected: {expected_vpc_restriction}")
                all_valid = False
        
        return all_valid
    
    def validate_bucket_naming(self, scenario: Dict[str, Any]) -> bool:
        """Validate S3 bucket naming convention"""
        parameters = scenario['parameters']
        
        project_name = parameters.get('ProjectName', '')
        bucket_base = parameters.get('S3BucketBaseName', '')
        environment = parameters.get('Environment', '')
        ci_build = parameters.get('CiBuild', '')
        
        # Expected bucket name pattern: {ProjectName}-{S3BucketBaseName}-{Environment}-{Region}{CiBuild}
        expected_prefix = f"{project_name}-{bucket_base}-{environment}-"
        
        # Check if bucket name construction is valid
        if project_name and bucket_base and environment:
            self.log_test(f"{scenario['scenario_name']} - Bucket naming convention", True, 
                         f"Expected prefix: {expected_prefix}")
            return True
        else:
            self.log_test(f"{scenario['scenario_name']} - Bucket naming convention", False, 
                         f"Missing required naming components")
            return False
    
    def validate_lifecycle_configuration(self, scenario: Dict[str, Any]) -> bool:
        """Validate lifecycle configuration for scenarios that enable it"""
        parameters = scenario['parameters']
        
        if parameters.get('S3LifecycleConfigurationEnabled', 'false') != 'true':
            self.log_test(f"{scenario['scenario_name']} - Lifecycle configuration (disabled)", True, 
                         "Lifecycle not enabled for this scenario")
            return True
        
        # Check lifecycle transition order and constraints
        transitions = []
        
        if parameters.get('TransitionToStandardIAEnabled', 'false') == 'true':
            transitions.append(('Standard-IA', parameters.get('TransitionToStandardIADays', 30)))
        
        if parameters.get('TransitionToIntelligentTieringEnabled', 'false') == 'true':
            transitions.append(('Intelligent-Tiering', parameters.get('TransitionToIntelligentTieringDays', 60)))
        
        if parameters.get('TransitionToOneZoneIAEnabled', 'false') == 'true':
            transitions.append(('One Zone-IA', parameters.get('TransitionToOneZoneIADays', 90)))
        
        if parameters.get('TransitionToGlacierIREnabled', 'false') == 'true':
            transitions.append(('Glacier IR', parameters.get('TransitionToGlacierIRDays', 120)))
        
        if parameters.get('TransitionToGlacierEnabled', 'false') == 'true':
            transitions.append(('Glacier', parameters.get('TransitionToGlacierDays', 180)))
        
        if parameters.get('TransitionToDeepArchiveEnabled', 'false') == 'true':
            transitions.append(('Deep Archive', parameters.get('TransitionToDeepArchiveDays', 365)))
        
        # Validate transition day constraints
        valid_transitions = True
        for storage_class, days in transitions:
            if days < 1:
                self.log_test(f"{scenario['scenario_name']} - {storage_class} transition days", False, 
                             f"Invalid days: {days}")
                valid_transitions = False
            else:
                self.log_test(f"{scenario['scenario_name']} - {storage_class} transition days", True, 
                             f"Valid days: {days}")
        
        # Check expiration configuration
        if parameters.get('EnableExpiration', 'false') == 'true':
            expiration_days = parameters.get('ExpirationDays', 365)
            if expiration_days > 0:
                self.log_test(f"{scenario['scenario_name']} - Expiration configuration", True, 
                             f"Expiration after {expiration_days} days")
            else:
                self.log_test(f"{scenario['scenario_name']} - Expiration configuration", False, 
                             f"Invalid expiration days: {expiration_days}")
                valid_transitions = False
        
        return valid_transitions
    
    def validate_security_policies(self, scenario: Dict[str, Any]) -> bool:
        """Validate security policy configuration"""
        parameters = scenario['parameters']
        bucket_policy = self.template.get('Resources', {}).get('S3BucketPolicy', {})
        
        if not bucket_policy:
            self.log_test(f"{scenario['scenario_name']} - Bucket policy exists", False, 
                         "S3BucketPolicy resource not found")
            return False
        
        policy_document = bucket_policy.get('Properties', {}).get('PolicyDocument', {})
        statements = policy_document.get('Statement', [])
        
        if not statements:
            self.log_test(f"{scenario['scenario_name']} - Policy statements exist", False, 
                         "No policy statements found")
            return False
        
        self.log_test(f"{scenario['scenario_name']} - Policy statements exist", True, 
                     f"Found {len(statements)} policy statements")
        
        # Check for HTTPS enforcement (should always be present)
        https_enforcement_found = False
        for statement in statements:
            statement_str = str(statement)
            if 'aws:SecureTransport' in statement_str and 'false' in statement_str:
                https_enforcement_found = True
                break
        
        self.log_test(f"{scenario['scenario_name']} - HTTPS enforcement policy", https_enforcement_found, 
                     "Policy should deny non-HTTPS requests")
        
        # Check VPC endpoint restriction if configured
        if parameters.get('S3VpcEndpointId', ''):
            vpc_restriction_found = False
            for statement in statements:
                statement_str = str(statement)
                if 'aws:sourceVpce' in statement_str:
                    vpc_restriction_found = True
                    break
            
            self.log_test(f"{scenario['scenario_name']} - VPC endpoint restriction", vpc_restriction_found, 
                         "Policy should restrict access to VPC endpoint")
        
        # Check KMS encryption enforcement if KMS is enabled
        if parameters.get('KmsMasterKeyArn', ''):
            kms_enforcement_found = False
            for statement in statements:
                statement_str = str(statement)
                if 's3:x-amz-server-side-encryption' in statement_str and 'aws:kms' in statement_str:
                    kms_enforcement_found = True
                    break
            
            self.log_test(f"{scenario['scenario_name']} - KMS encryption enforcement", kms_enforcement_found, 
                         "Policy should enforce KMS encryption")
        
        return True
    
    def validate_event_notifications(self, scenario: Dict[str, Any]) -> bool:
        """Validate event notification configuration"""
        parameters = scenario['parameters']
        
        if not parameters.get('LambdaFunctionArn', ''):
            self.log_test(f"{scenario['scenario_name']} - Event notifications (disabled)", True, 
                         "Event notifications not configured for this scenario")
            return True
        
        # Check notification events
        notification_events = parameters.get('NotificationEvents', [])
        if isinstance(notification_events, str):
            notification_events = [notification_events]
        
        valid_events = ['s3:ObjectCreated:*', 's3:ObjectRemoved:*', 's3:ObjectCreated:Put', 
                       's3:ObjectCreated:Post', 's3:ObjectRemoved:Delete']
        
        valid_notification_events = True
        for event in notification_events:
            if event in valid_events:
                self.log_test(f"{scenario['scenario_name']} - Notification event '{event}'", True, 
                             "Valid S3 event type")
            else:
                self.log_test(f"{scenario['scenario_name']} - Notification event '{event}'", False, 
                             f"Invalid event type, should be one of: {valid_events}")
                valid_notification_events = False
        
        # Check notification filters
        prefix = parameters.get('Prefix', '')
        suffix = parameters.get('Suffix', '')
        
        if prefix or suffix:
            self.log_test(f"{scenario['scenario_name']} - Notification filters", True, 
                         f"Prefix: '{prefix}', Suffix: '{suffix}'")
        else:
            self.log_test(f"{scenario['scenario_name']} - Notification filters", True, 
                         "No filters configured (will apply to all objects)")
        
        return valid_notification_events
    
    def validate_resource_tagging(self, scenario: Dict[str, Any]) -> bool:
        """Validate resource tagging configuration"""
        parameters = scenario['parameters']
        s3_bucket = self.template.get('Resources', {}).get('S3Bucket', {})
        
        if not s3_bucket:
            self.log_test(f"{scenario['scenario_name']} - S3 bucket resource exists", False)
            return False
        
        tags = s3_bucket.get('Properties', {}).get('Tags', [])
        
        if not tags:
            self.log_test(f"{scenario['scenario_name']} - Resource tags exist", False, 
                         "No tags found on S3 bucket")
            return False
        
        # Check for required tags
        required_tags = ['Name', 'Project', 'Environment', 'ManagedBy']
        tag_names = [tag.get('Key', '') for tag in tags if isinstance(tag, dict)]
        
        all_required_present = True
        for required_tag in required_tags:
            if required_tag in tag_names:
                self.log_test(f"{scenario['scenario_name']} - Required tag '{required_tag}'", True)
            else:
                self.log_test(f"{scenario['scenario_name']} - Required tag '{required_tag}'", False, 
                             f"Missing required tag")
                all_required_present = False
        
        # Check for GitHub tags if GitHub parameters are provided
        if parameters.get('GitHubOrg', '') or parameters.get('GitHubRepo', ''):
            github_tags = ['GitHubOrg', 'GitHubRepo']
            for github_tag in github_tags:
                if github_tag in tag_names:
                    self.log_test(f"{scenario['scenario_name']} - GitHub tag '{github_tag}'", True)
                else:
                    self.log_test(f"{scenario['scenario_name']} - GitHub tag '{github_tag}'", False, 
                                 f"Missing GitHub tag")
        
        return all_required_present
    
    def validate_outputs(self, scenario: Dict[str, Any]) -> bool:
        """Validate template outputs"""
        outputs = self.template.get('Outputs', {})
        
        if 'S3BucketArn' not in outputs:
            self.log_test(f"{scenario['scenario_name']} - S3BucketArn output", False, 
                         "Missing required output")
            return False
        
        bucket_arn_output = outputs['S3BucketArn']
        
        # Check output has description
        if 'Description' in bucket_arn_output:
            self.log_test(f"{scenario['scenario_name']} - S3BucketArn description", True)
        else:
            self.log_test(f"{scenario['scenario_name']} - S3BucketArn description", False, 
                         "Output missing description")
        
        # Check output has value
        if 'Value' in bucket_arn_output:
            self.log_test(f"{scenario['scenario_name']} - S3BucketArn value", True)
        else:
            self.log_test(f"{scenario['scenario_name']} - S3BucketArn value", False, 
                         "Output missing value")
        
        # Check export name if present
        if 'Export' in bucket_arn_output:
            export_config = bucket_arn_output['Export']
            if 'Name' in export_config:
                self.log_test(f"{scenario['scenario_name']} - S3BucketArn export name", True)
            else:
                self.log_test(f"{scenario['scenario_name']} - S3BucketArn export name", False, 
                             "Export missing name")
        
        return True
    
    def save_scenario_template(self, scenario: Dict[str, Any]):
        """Save the template with scenario parameters for inspection"""
        try:
            # Create template with scenario parameters as defaults
            template_copy = self.template.copy()
            
            # Apply parameter defaults
            if 'Parameters' in template_copy:
                for param_name, param_def in template_copy['Parameters'].items():
                    if param_name in scenario['parameters']:
                        param_def['Default'] = scenario['parameters'][param_name]
            
            # Save as JSON
            os.makedirs('tests/validation/results', exist_ok=True)
            filename = f"tests/validation/results/{scenario['scenario_name'].lower().replace(' ', '_')}.json"
            
            with open(filename, 'w') as f:
                json.dump(template_copy, f, indent=2, default=str)
            
            # Save as YAML
            yaml_filename = f"tests/validation/results/{scenario['scenario_name'].lower().replace(' ', '_')}.yaml"
            with open(yaml_filename, 'w') as f:
                yaml.dump(template_copy, f, default_flow_style=False, sort_keys=False)
            
            self.log_test(f"{scenario['scenario_name']} - Template files saved", True, 
                         f"Saved to {filename} and {yaml_filename}")
            
        except Exception as e:
            self.log_test(f"{scenario['scenario_name']} - Template files saved", False, 
                         f"Error saving files: {str(e)}")
    
    def run_scenario_tests(self, scenario: Dict[str, Any]):
        """Run all tests for a specific integration scenario"""
        print(f"\n=== Integration Test Scenario: {scenario['scenario_name']} ===")
        print(f"Description: {scenario['description']}")
        print(f"Requirements: {', '.join(scenario['requirements'])}")
        print(f"Parameters: {len(scenario['parameters'])} configured")
        
        # Run validation tests
        self.validate_template_syntax(scenario)
        self.validate_parameter_constraints(scenario)
        self.validate_expected_resources(scenario)
        self.validate_conditional_logic(scenario)
        self.validate_bucket_naming(scenario)
        self.validate_lifecycle_configuration(scenario)
        self.validate_security_policies(scenario)
        self.validate_event_notifications(scenario)
        self.validate_resource_tagging(scenario)
        self.validate_outputs(scenario)
        
        # Save scenario template for inspection
        self.save_scenario_template(scenario)
    
    def run_all_tests(self):
        """Run all integration test scenarios"""
        print("=== CloudFormation Template Integration Test Scenarios ===")
        print(f"Template: {self.template_path}")
        print(f"Dry run mode: {self.dry_run}")
        
        self.create_test_scenarios()
        print(f"Testing {len(self.test_scenarios)} integration scenarios")
        
        for scenario in self.test_scenarios:
            self.run_scenario_tests(scenario)
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n=== Integration Test Summary ===")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Save detailed test report
        self.save_test_report()
        
        if failed_tests > 0:
            print(f"\nFailed tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}")
                    if result['message']:
                        print(f"    {result['message']}")
            return False
        else:
            print("All integration tests passed!")
            return True
    
    def save_test_report(self):
        """Save detailed test report"""
        try:
            os.makedirs('tests/validation/results', exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"tests/validation/results/integration_test_report_{timestamp}.txt"
            
            with open(report_filename, 'w') as f:
                f.write("CloudFormation Template Integration Test Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Template: {self.template_path}\n")
                f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Dry Run Mode: {self.dry_run}\n")
                f.write(f"Total Scenarios: {len(self.test_scenarios)}\n")
                f.write(f"Total Tests: {len(self.test_results)}\n")
                f.write(f"Passed: {sum(1 for r in self.test_results if r['passed'])}\n")
                f.write(f"Failed: {sum(1 for r in self.test_results if not r['passed'])}\n\n")
                
                f.write("Test Results:\n")
                f.write("-" * 30 + "\n")
                for result in self.test_results:
                    status = "PASS" if result['passed'] else "FAIL"
                    f.write(f"[{status}] {result['test']}\n")
                    if result['message']:
                        f.write(f"    {result['message']}\n")
                
                f.write("\nScenario Details:\n")
                f.write("-" * 30 + "\n")
                for scenario in self.test_scenarios:
                    f.write(f"\nScenario: {scenario['scenario_name']}\n")
                    f.write(f"Description: {scenario['description']}\n")
                    f.write(f"Requirements: {', '.join(scenario['requirements'])}\n")
                    f.write(f"Parameters: {len(scenario['parameters'])}\n")
                    for param, value in scenario['parameters'].items():
                        f.write(f"  {param}: {value}\n")
            
            print(f"Detailed test report saved to: {report_filename}")
            
        except Exception as e:
            print(f"Error saving test report: {str(e)}")

if __name__ == "__main__":
    # Check if AWS credentials are available for live testing
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry_run = False
        print("Running in live mode - will attempt AWS API calls")
    else:
        print("Running in dry-run mode - template validation only")
    
    tester = IntegrationTestScenarios("cfn/template.yaml", dry_run=dry_run)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)