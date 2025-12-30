pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  environment {
    COMPOSE_PROJECT_NAME = "python-intro-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Build') {
      steps {
        sh '''
          #!/usr/bin/env bash
          set -eu

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
          docker-compose build
        '''
      }
    }

    stage('Test') {
      steps {
        sh '''
          #!/usr/bin/env bash
          set -eu

          docker-compose up -d
          docker-compose ps

          docker exec script python -m pytest -q tests/
        '''
      }
      post {
        always {
          sh '''
            #!/usr/bin/env bash
            set +e
            docker-compose down -v || true
          '''
        }
      }
    }

    
    stage('Deploy') {
      steps {
        sh '''
          #!/usr/bin/env bash
          set -eu
          docker-compose up -d
          docker-compose ps
        '''
      }
    }
  }
}
