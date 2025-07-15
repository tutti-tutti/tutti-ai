pipeline {
    agent any

    environment {
        IMAGE_NAME = "shop-review"
        TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${TAG}")
                }
            }
        }
        stage('Test') {
            steps {
                sh 'pip install --upgrade pip && pip install .'
                sh 'pytest'
            }
        }
        stage('Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    script {
                        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                            docker.image("${IMAGE_NAME}:${TAG}").push()
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
} 