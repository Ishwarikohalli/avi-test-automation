pipeline {
    agent any
    
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
                script {
                    // Changed from python3 to python
                    sh 'python -m venv venv'
                    
                    sh '''
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                    '''
                }
            }
        }
        
        stage('Run Automation') {
            steps {
                script {
                    sh '''
                        . venv/bin/activate
                        python main.py --config config.yml
                    '''
                }
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
