pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  parameters {
    booleanParam(name: 'DEPLOY_ENABLED', defaultValue: false, description: 'Enable deploy stage (usually only from main branch)')
    string(name: 'DEPLOY_HOST', defaultValue: '', description: 'Deploy server host (e.g. 1.2.3.4)')
    string(name: 'DEPLOY_PATH', defaultValue: '/opt/python_introduction', description: 'Remote path to deploy into')
  }

  environment {
    COMPOSE_PROJECT_NAME = "python-intro-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Build') {
      steps {
        sh '''
          set -euo pipefail

          if [ ! -f .env ]; then
            cat > .env <<'EOF'
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=postgres
EOF
          fi

          docker-compose version
          docker-compose build --pull
        '''
      }
    }

    stage('Test') {
      steps {
        sh '''
          set -euo pipefail

          docker-compose up -d --build
          docker-compose ps

          docker exec script python -m pytest -q tests/
        '''
      }
      post {
        always {
          sh '''
            set +e
            docker-compose logs --no-color || true
            docker-compose down -v || true
          '''
        }
      }
    }

    stage('Deploy') {
      when {
        allOf {
          branch 'main'
          expression { return params.DEPLOY_ENABLED }
          expression { return params.DEPLOY_HOST?.trim() }
        }
      }
      steps {
        withCredentials([
          sshUserPrivateKey(credentialsId: 'deploy-ssh-key', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')
        ]) {
          sh '''
            set -euo pipefail

            tar -czf app.tgz --exclude .git --exclude .pytest_cache --exclude __pycache__ .

            scp -i "$SSH_KEY" -o StrictHostKeyChecking=no app.tgz "$SSH_USER@${DEPLOY_HOST}:/tmp/python_introduction-${BUILD_NUMBER}.tgz"

            ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@${DEPLOY_HOST}" \
              "mkdir -p '${DEPLOY_PATH}' && \
               tar -xzf '/tmp/python_introduction-${BUILD_NUMBER}.tgz' -C '${DEPLOY_PATH}' && \
               cd '${DEPLOY_PATH}' && \
               docker-compose up -d --build"
          '''
        }
      }
    }
  }
}
