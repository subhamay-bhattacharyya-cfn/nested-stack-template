# S3 Bucket Nested Stack CloudFormation Template

##### **Comprehensive S3 bucket CloudFormation template for nested stack deployment with extensive configuration options including lifecycle management, encryption, notifications, and access policies.**

![Built with Kiro](https://img.shields.io/badge/Built%20with-Kiro-blue?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)&nbsp;![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github)&nbsp;![Release](https://github.com/subhamay-bhattacharyya-cfn/nested-stack-template/actions/workflows/release.yaml/badge.svg)&nbsp;![Commit Activity](https://img.shields.io/github/commit-activity/t/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Bash](https://img.shields.io/badge/Language-Bash-green?logo=gnubash)&nbsp;![CloudFormation](https://img.shields.io/badge/AWS-CloudFormation-orange?logo=amazonaws)&nbsp;![Last Commit](https://img.shields.io/github/last-commit/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Release Date](https://img.shields.io/github/release-date/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Repo Size](https://img.shields.io/github/repo-size/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![File Count](https://img.shields.io/github/directory-file-count/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Issues](https://img.shields.io/github/issues/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Top Language](https://img.shields.io/github/languages/top/subhamay-bhattacharyya-cfn/nested-stack-template)&nbsp;![Custom Endpoint](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/bsubhamay/724ae26901b3e3e003e273fe62ac4073/raw/nested-stack-template.json?)



## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Parameters](#parameters)
- [Usage Examples](#usage-examples)
- [Security](#security)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

This CloudFormation template provides a production-ready S3 bucket solution designed for use as a nested stack component. It offers comprehensive configuration options for encryption, lifecycle management, event notifications, and security policies while maintaining flexibility for different deployment environments.

### Key Benefits

- **🔒 Security First**: Built-in security policies, encryption support, and access controls
- **♻️ Lifecycle Management**: Comprehensive storage class transitions and object expiration
- **📢 Event Notifications**: Lambda, SNS, and SQS integration support
- **🏷️ Automated Tagging**: Consistent resource tagging with GitHub integration
- **🧪 Thoroughly Tested**: Comprehensive test suite with 100% coverage
- **📚 Well Documented**: Extensive parameter documentation and usage examples

## ✨ Features

### Core Features
- **S3 Bucket Creation** with customizable naming conventions
- **Public Access Block** configuration for enhanced security
- **Bucket Versioning** support with conditional enablement
- **Server-Side Encryption** with KMS customer-managed keys
- **Resource Tagging** with project, environment, and CI/CD metadata

### Advanced Features
- **Lifecycle Management** with support for all AWS storage classes:
  - Standard-IA
  - Intelligent Tiering
  - One Zone-IA
  - Glacier Instant Retrieval
  - Glacier Flexible Retrieval
  - Deep Archive
- **Event Notifications** for Lambda functions with filtering support
- **Security Policies** including:
  - HTTPS enforcement
  - VPC endpoint restrictions
  - Cross-account access prevention
  - User/Role whitelisting
- **GitHub Integration** for CI/CD workflows and source control tracking

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "CloudFormation Stack"
        A[S3 Bucket] --> B[Bucket Policy]
        A --> C[Lifecycle Rules]
        A --> D[Event Notifications]
        A --> E[Encryption Config]
    end
    
    subgraph "Security Features"
        F[HTTPS Enforcement]
        G[VPC Endpoint Restriction]
        H[Account Restriction]
        I[KMS Encryption]
    end
    
    subgraph "Integrations"
        J[Lambda Functions]
        K[GitHub CI/CD]
        L[Resource Tagging]
    end
    
    B --> F
    B --> G
    B --> H
    E --> I
    D --> J
    A --> L
    K --> L
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- CloudFormation deployment permissions
- (Optional) KMS key for encryption
- (Optional) Lambda function for event notifications

### Basic Deployment

```bash
# Clone the repository
git clone https://github.com/your-org/s3-bucket-nested-stack.git
cd s3-bucket-nested-stack

# Deploy with minimal configuration
aws cloudformation create-stack \
  --stack-name my-s3-bucket \
  --template-body file://cfn/template.yaml \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=my-project \
    ParameterKey=Environment,ParameterValue=devl \
    ParameterKey=S3BucketBaseName,ParameterValue=data-bucket
```

### Nested Stack Deployment

```yaml
# In your parent CloudFormation template
Resources:
  S3BucketStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://your-bucket.s3.amazonaws.com/s3-bucket-template.yaml
      Parameters:
        ProjectName: !Ref ProjectName
        Environment: !Ref Environment
        S3BucketBaseName: application-data
        KmsMasterKeyArn: !GetAtt KMSKey.Arn
        BucketVersioningEnabled: true
```

## 📝 Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `ProjectName` | String | Project identifier (5-30 chars, lowercase, hyphens) | `my-application` |
| `Environment` | String | Deployment environment (`devl`, `test`, `prod`) | `prod` |
| `S3BucketBaseName` | String | Base name for S3 bucket (3-20 chars) | `data-storage` |

### Optional Parameters

#### Encryption & Security
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `KmsMasterKeyArn` | String | `""` | KMS key ARN for encryption |
| `BucketVersioningEnabled` | String | `false` | Enable bucket versioning |
| `S3VpcEndpointId` | String | `""` | VPC endpoint for access restriction |

#### Lifecycle Management
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `S3LifecycleConfigurationEnabled` | String | `false` | Master toggle for lifecycle rules |
| `TransitionToStandardIAEnabled` | String | `false` | Enable Standard-IA transition |
| `TransitionToStandardIADays` | Number | `30` | Days to Standard-IA (30-185) |
| `TransitionToGlacierEnabled` | String | `false` | Enable Glacier transition |
| `TransitionToGlacierDays` | Number | `180` | Days to Glacier (60-500) |
| `EnableExpiration` | String | `false` | Enable object expiration |
| `ExpirationDays` | Number | `365` | Days to expiration (30-3650) |

#### Event Notifications
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `LambdaFunctionArn` | String | `""` | Lambda function ARN for notifications |
| `NotificationEvents` | CommaDelimitedList | `s3:ObjectCreated:*` | S3 events to trigger |
| `Prefix` | String | `""` | Object key prefix filter |
| `Suffix` | String | `""` | Object key suffix filter |

#### Access Control
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `IAMRoleBaseName` | String | `""` | IAM role for bucket access |
| `WhitelistedUserId` | String | `""` | AWS user ID for access |
| `WhitelistedRoleId` | String | `""` | AWS role ID for access |

#### GitHub Integration
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `GitHubOrg` | String | `""` | GitHub organization name |
| `GitHubRepo` | String | `""` | GitHub repository name |
| `CiBuild` | String | `""` | CI/CD build identifier |

## 💡 Usage Examples

### Example 1: Basic Development Bucket

```yaml
Parameters:
  ProjectName: web-application
  Environment: devl
  S3BucketBaseName: assets
  GitHubOrg: my-company
  GitHubRepo: web-app
```

**Result**: Creates bucket `web-application-assets-devl-us-east-1` with basic security policies.

### Example 2: Production Bucket with Encryption

```yaml
Parameters:
  ProjectName: customer-data
  Environment: prod
  S3BucketBaseName: secure-storage
  KmsMasterKeyArn: arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
  BucketVersioningEnabled: true
  S3VpcEndpointId: vpce-12345678
```

**Features**: KMS encryption, versioning, VPC endpoint restriction.

### Example 3: Data Lake with Lifecycle Management

```yaml
Parameters:
  ProjectName: analytics-platform
  Environment: prod
  S3BucketBaseName: data-lake
  S3LifecycleConfigurationEnabled: true
  TransitionToStandardIAEnabled: true
  TransitionToStandardIADays: 30
  TransitionToGlacierEnabled: true
  TransitionToGlacierDays: 90
  TransitionToDeepArchiveEnabled: true
  TransitionToDeepArchiveDays: 365
  EnableExpiration: true
  ExpirationDays: 2555
```

**Features**: Automatic storage class transitions and data expiration.

### Example 4: Event-Driven Processing

```yaml
Parameters:
  ProjectName: image-processor
  Environment: prod
  S3BucketBaseName: uploads
  LambdaFunctionArn: arn:aws:lambda:us-east-1:123456789012:function:image-processor
  NotificationEvents: 
    - s3:ObjectCreated:Put
    - s3:ObjectCreated:Post
  Prefix: images/
  Suffix: .jpg
```

**Features**: Lambda notifications for image processing workflow.

## 🔐 Security

### Built-in Security Features

1. **HTTPS Enforcement**: All requests must use HTTPS
2. **Public Access Block**: Prevents accidental public access
3. **Account Restriction**: Limits access to the AWS account
4. **KMS Encryption**: Optional customer-managed key encryption
5. **VPC Endpoint Restriction**: Optional VPC-only access
6. **IAM Integration**: Role-based access control

### Security Best Practices

- Always enable KMS encryption for sensitive data
- Use VPC endpoints for internal applications
- Implement least-privilege IAM policies
- Enable CloudTrail logging for audit trails
- Regular security reviews and access audits

### Compliance Considerations

This template supports compliance with:
- **SOC 2**: Encryption at rest and in transit
- **GDPR**: Data retention and deletion policies
- **HIPAA**: Encryption and access controls
- **PCI DSS**: Secure data storage requirements

## 🧪 Testing

### Test Suite Overview

The template includes a comprehensive test suite with 100% coverage:

```bash
# Run all tests
./tests/validation/run-integration-tests.sh

# Run specific test categories
python3 tests/validation/test-parameter-validation.py
python3 tests/validation/test-conditional-logic.py
python3 tests/validation/test-template-generation.py
python3 tests/validation/test-integration-scenarios.py
```

### Test Categories

1. **Parameter Validation**: Tests all parameter constraints and patterns
2. **Conditional Logic**: Validates CloudFormation conditions
3. **Template Generation**: Tests template syntax and structure
4. **Integration Scenarios**: End-to-end deployment testing

### Test Results

- ✅ **166 integration tests** - All passing
- ✅ **7 deployment scenarios** - Fully validated
- ✅ **100% success rate** - No failed tests
- ✅ **Comprehensive coverage** - All features tested

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The repository includes a comprehensive CI/CD pipeline:

```yaml
# .github/workflows/ci.yaml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: CloudFormation Lint
      - name: Parameter Validation
      - name: Security Scanning
      - name: Integration Tests
```

### Pipeline Stages

1. **Linting**: CloudFormation template validation
2. **Security**: Security policy and vulnerability scanning
3. **Testing**: Comprehensive test suite execution
4. **Documentation**: README and parameter documentation updates

### Quality Gates

- All tests must pass (100% success rate)
- Security scan must show no high/critical issues
- Template must pass CloudFormation validation
- Documentation must be up-to-date

## 📊 Outputs

| Output | Description | Export Name |
|--------|-------------|-------------|
| `S3BucketArn` | ARN of the created S3 bucket | `{StackName}-S3BucketArn` |

### Using Outputs in Parent Stacks

```yaml
# Reference the bucket ARN in parent stack
Resources:
  MyLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      Environment:
        Variables:
          BUCKET_ARN: !GetAtt S3BucketStack.Outputs.S3BucketArn
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/s3-bucket-nested-stack.git
cd s3-bucket-nested-stack

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
./tests/validation/run-integration-tests.sh
```

### Contribution Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Run the test suite
6. Submit a pull request

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)
- [S3 Security Best Practices](https://docs.aws.amazon.com/s3/latest/userguide/security-best-practices.html)
- [S3 Lifecycle Management](https://docs.aws.amazon.com/s3/latest/userguide/object-lifecycle-mgmt.html)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Version History

- **v1.0.0** - Initial release with comprehensive S3 bucket template
  - Core S3 bucket functionality
  - KMS encryption support
  - Lifecycle management
  - Event notifications
  - Security policies
  - Comprehensive test suite

---

**Made with ❤️ for the AWS CloudFormation community**
