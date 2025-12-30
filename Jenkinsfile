pipeline {
    agent any
    
    environment {
        DOCKER_COMPOSE = 'docker-compose'
        PROJECT_NAME = 'python-intro'
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                
                // Checkout the code from SCM
                checkout scm
                
                // Print the current branch and commit
                sh 'git branch'
                sh 'git rev-parse HEAD'
            }
        }
        
        stage('Build') {
            steps {
                script {
                    // Build Docker images
                    sh "${DOCKER_COMPOSE} -p ${PROJECT_NAME} build"
                }
            }
        }
        
        stage('Test') {
            environment {
                // Set test environment variables
                PYTHONPATH = "${WORKSPACE}"
                TEST_DB_NAME = "test_${BUILD_NUMBER}"
            }
            
            steps {
                script {
                    try {
                        // Create test database
                        sh "createdb -h localhost -U postgres ${TEST_DB_NAME} || true"
                        
                        // Run tests with coverage
                        sh """
                        ${DOCKER_COMPOSE} -p ${PROJECT_NAME} run --rm \
                            -e DB_NAME=${TEST_DB_NAME} \
                            -e PYTHONPATH=/app \
                            app sh -c \
                            "pip install -r requirements-dev.txt && \
                             python -m pytest tests/ -v --cov=script --cov-report=xml:coverage.xml"
                        """
                        
                        // Archive test results
                        junit '**/test-reports/*.xml'
                        
                        // Publish coverage report
                        publishHTML(target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: false,
                            keepAll: true,
                            reportDir: 'htmlcov',
                            reportFiles: 'index.html',
                            reportName: 'Coverage Report'
                        ])
                        
                        // Publish coverage to Jenkins
                        publishCoverage(
                            adapters: [coberturaAdapter('coverage.xml')],
                            sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                        )
                    } finally {
                        // Cleanup test database
                        sh "dropdb -h localhost -U postgres ${TEST_DB_NAME} || true"
                    }
                }
            }
            
            post {
                always {
                    // Clean up any running containers
                    sh "${DOCKER_COMPOSE} -p ${PROJECT_NAME} down --remove-orphans"
                }
            }
        }
        
        stage('Deploy') {
            when {
                // Only deploy from main branch
                branch 'main'
            }
            
            steps {
                script {
                    // Push images to registry (example for Docker Hub)
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-hub-credentials',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )]) {
                        sh """
                        # Login to Docker Hub
                        echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
                        
                        # Tag and push images
                        ${DOCKER_COMPOSE} -p ${PROJECT_NAME} build
                        
                        # Example: Tag and push the app image
                        docker tag ${PROJECT_NAME}_app ${DOCKER_USERNAME}/${PROJECT_NAME}:${BUILD_NUMBER}
                        docker tag ${PROJECT_NAME}_app ${DOCKER_USERNAME}/${PROJECT_NAME}:latest
                        
                        docker push ${DOCKER_USERNAME}/${PROJECT_NAME}:${BUILD_NUMBER}
                        docker push ${DOCKER_USERNAME}/${PROJECT_NAME}:latest
                        """
                    }
                    
                    // Example: Deploy to a server using SSH
                    sshagent(['deploy-key']) {
                        sh """
                        # Example deployment commands
                        ssh -o StrictHostKeyChecking=no user@your-server.com \
                            "docker-compose -f /path/to/project/docker-compose.prod.yml pull && \
                             docker-compose -f /path/to/project/docker-compose.prod.yml up -d"
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up workspace
            cleanWs()
            
            // Clean up Docker resources
            sh "${DOCKER_COMPOSE} -p ${PROJECT_NAME} down --remove-orphans --volumes"
        }
        
        success {
            // Notify on success
            echo 'Build, test, and deploy completed successfully!'
        }
        
        failure {
            // Notify on failure
            echo 'Pipeline failed. Please check the logs for details.'
        }
    }
}
