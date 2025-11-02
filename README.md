Here's the updated README.md with comprehensive Jenkins setup instructions and required plugins:

# Test Automation Framework with Jenkins CI/CD

## Overview
Python-based automation framework integrated with Jenkins for continuous testing. This framework performs API testing with parallel execution, YAML-driven configuration, and comprehensive CI/CD pipeline integration.

## Features
- REST API testing with parallel execution
- YAML-driven configuration
- Jenkins CI/CD pipeline integration
- Virtual environment isolation
- Email notifications on build status
- Cron-based scheduled execution
- Mock SSH/RDP bot integrations

## Project Structure
test_automation/
├── Jenkinsfile                    # Jenkins pipeline definition
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── main.py                       # Main automation framework
├── config.yml                    # YAML configuration
├── src/
│   ├── __init__.py
│   ├── api_client.py             # API client for REST operations
│   ├── test_cases.py             # Test case definitions and execution
│   └── utils.py                  # Utility functions
└── docs/                         # Documentation and screenshots
    ├── jenkins-pipeline-success.png
    ├── jenkins-stage-view.png
    ├── jenkins-console-output.png
    └── jenkins-job-config.png
## Jenkins Setup Instructions

### 1. Deploy Jenkins Container

# Deploy Jenkins with persistent storage
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_data:/var/jenkins_home jenkins/jenkins:lts-jdk11

### 2. Initial Jenkins Setup
1. **Access Jenkins**: Open `http://localhost:8080` in your browser
2. **Get Admin Password**:
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
  
3. **Install Plugins**: Choose "Install suggested plugins"
4. **Create Admin User**: Set up your administrator account
5. **Instance Configuration**: Use default URL `http://localhost:8080`

### 3. Required Jenkins Plugins

Install these plugins via **Manage Jenkins** → **Plugins** → **Available plugins**:

#### Essential Plugins:
- **Pipeline** - For defining CI/CD pipelines
- **Git** - For source code management
- **Email Extension** - For build notifications (optional)

#### Recommended Plugins:
- **Blue Ocean** - Modern UI for pipelines
- **Build Timeout** - Automatically cancel stuck builds
- **Workspace Cleanup** - Clean workspace after build

### 4. Install Python in Jenkins Container

### 5. Pipeline Configuration

#### Create New Pipeline Job:
1. **Dashboard** → **New Item**
2. Enter name: `test-automation-pipeline`
3. Select **Pipeline** → **OK**

#### Configure Pipeline:
1. **Description**: "Automated test execution pipeline"
2. **Pipeline Section**:
   - Definition: `Pipeline script from SCM`
   - SCM: `Git`
   - Repository URL: `https://github.com/Ishwarikohalli/avi-test-automation`
   - Script Path: `Jenkinsfile`
   - Branches: `*/main`

#### Build Triggers:
- **Manual**: "Build Now" button
- **Automatic**: Configured in Jenkinsfile to run hourly

### 6. Pipeline Stages Overview

The pipeline executes three main stages:

1. **Checkout**: Fetches latest code from Git repository
2. **Setup Environment**: Creates Python virtual environment and installs dependencies
3. **Run Automation**: Executes the test framework with configuration

## Jenkinsfile Pipeline Definition

pipeline {
    agent any
    triggers {
        cron('H * * * *')
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }  
        stage('Run Automation') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 main.py --config config.yml
                '''
            }
        }
    }    
    post {
        always {
            sh 'rm -rf venv'
        }
        success {
            echo 'Build completed successfully!'
        }
        failure {
            echo 'Build failed! Check console output for details.'
        }
    }
}


## Local Development

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate    

# Install dependencies
pip install -r requirements.txt

# Run framework locally
python main.py --config config.yml

## Configuration

Edit `config.yml` to customize:
- API endpoints and credentials
- Test parameters and timeouts
- Parallel execution settings
- Virtual service configurations

## Test Execution Details

The framework performs:
- **API Validation**: GET/PUT operations on virtual services
- **Pre/Post Validation**: State verification before and after operations
- **Mock Bot Integration**: SSH and RDP connection simulations
- **Parallel Execution**: Multiple test cases running concurrently
- **Comprehensive Logging**: Detailed execution logs with timestamps

## Monitoring and Troubleshooting

### Checking Pipeline Status
- **Stage View**: Visual pipeline execution status
- **Console Output**: Detailed execution logs
- **Build History**: Historical build performance

### Common Issues
1. **Python not found**: Ensure Python is installed in Jenkins container
2. **Git authentication**: Verify repository URL and access permissions
3. **Dependency issues**: Check requirements.txt and virtual environment setup

## Success Metrics
-  All pipeline stages execute successfully
-  Tests complete with 100% success rate
-  Virtual environment created and cleaned up properly
-  Build fails appropriately on test failures
-  Scheduled executions run automatically

## Support
For issues with Jenkins setup or pipeline execution, check:
1. Jenkins console output for detailed error messages
2. Container logs: `docker logs jenkins`
3. Python virtual environment setup in workspace

