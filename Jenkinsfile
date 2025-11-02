pipeline {
    agent {
        docker {
            image 'python:3.9-slim'
        }
    }
    
    triggers {
        cron('H * * * *')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    currentBuild.displayName = "BUILD-${env.BUILD_NUMBER}"
                    currentBuild.description = "Commit: ${env.GIT_COMMIT}"
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    python -m venv venv
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
                    python main.py --config config.yml
                '''
            }
        }
    }
    
    post {
        always {
            sh 'rm -rf venv'
            echo "Build ${currentBuild.result} - ${currentBuild.fullDisplayName}"
        }
    }
}
