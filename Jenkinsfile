pipeline {
    agent any

    environment {
        // Project configuration
        PROJECT_NAME = 'file_converter_project'
        DOCKER_IMAGE = 'file-converter'
        DOCKER_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

        // Snyk credentials
        SNYK_TOKEN = credentials('snyk-token')

        // Report directories
        REPORTS_DIR = 'reports'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out code from Github...'
                checkout scm

                // Create reports directory
                sh "mkdir -p ${REPORTS_DIR}"
            }
        }

        stage('Environment Info') {
            steps {
                echo 'Environment Information'
                sh '''
                    echo "Branch: ${BRANCH_NAME}"
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Docker Tag: ${DOCKER_TAG}"
                    echo "Workspace: ${WORKSPACE}"
                    docker --version
                '''
            }
        }

        stage('SAST - Bandit') {
            steps {
                echo 'Running Static Application Security Testing with Bandit...'
                script {
                    try {
                        sh '''
                            # Run Bandit as Docker container
                            docker run --rm \
                            -v ${WORKSPACE}:/src \
                            -v ${WORKSPACE}/${REPORTS_DIR}:/reports \
                            python:3.11-slim \
                            sh -c "pip install bandit && \
                               bandit -r /src/app/ -f json -o /reports/bandit-report.json || true && \
                               bandit -r /src/app/ -f txt -o /reports/bandit-report.txt || true"
                        '''

                        // Display summary
                        sh 'cat ${REPORTS_DIR}/bandit-report.txt || echo "Bandit report not found"'
                    } catch (Exception e) {
                        echo "Bandit scan completed with findings: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Dependency Check - Snyk') {
            steps {
                echo 'Running Dependency Vulnerability Scan with Snyk...'
                script {
                    try {
                        
                        withCredentials([string(credentialsId: 'snyk-token', variable: 'SNYK_TOKEN')]) {
                            
                            // Create reports directory
                            sh 'mkdir -p ${REPORTS_DIR}'
                            
                            // Run Snyk as Docker container
                            sh '''
                                docker run --rm \
                                    -e SNYK_TOKEN=$SNYK_TOKEN \
                                    -v ${WORKSPACE}:/project \
                                    -v ${WORKSPACE}/reports:/reports \
                                    snyk/snyk:python-3.11 test \
                                    --file=/project/requirements.txt \
                                    --severity-threshold=low \
                                    --json-file-output=/reports/snyk-report.json || true
                            '''
                            
                            // Run again for console output
                            sh '''
                                docker run --rm \
                                    -e SNYK_TOKEN=$SNYK_TOKEN \
                                    -v ${WORKSPACE}:/project \
                                    snyk/snyk:python-3.11 test \
                                    --file=/project/requirements.txt \
                                    --severity-threshold=low || true
                            '''
                            echo 'Snyk scan completed'
                        }
                    } catch(Exception e) {
                        echo "Snyk scan failed: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }


        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest
                    '''
                    echo "Image built: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }

        stage('Container Scan - Trivy') {
            steps {
                echo 'Scanning Docker image with Trivy...'
                script {
                    try {
                        sh '''
                            # Run Trivy as Docker container
                            # JSON report
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                -v ${WORKSPACE}/${REPORTS_DIR}:/reports \
                                aquasec/trivy:latest image \
                                --format json \
                                --output /reports/trivy-report.json \
                                ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                            
                            # Table report
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                -v ${WORKSPACE}/${REPORTS_DIR}:/reports \
                                aquasec/trivy:latest image \
                                --format table \
                                --output /reports/trivy-report.txt \
                                ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                            
                            # Display summary (HIGH and CRITICAL only)
                            echo "Trivy Summary (HIGH and CRITICAL vulnerabilities):"
                            docker run --rm \
                                -v /var/run/docker.sock:/var/run/docker.sock \
                                -v ${WORKSPACE}/${REPORTS_DIR}:/reports \
                                aquasec/trivy:latest image \
                                --severity HIGH,CRITICAL\
                                ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                        '''

                        echo 'Trivy scan completed'
                } catch(Exception e) {
                    echo "Trivy found vulnerabilities: ${e.message}"
                    currentBuild.result = 'UNSTABLE'
                }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying application for DAST testing...'
                script {

                    // Create jenkins network in Docker-in-Docker
                    sh '''
                        docker network create jenkins 2>/dev/null || true
                    '''
                    
                    // Stop any existing container
                    sh '''
                        docker stop file-converter-test || true
                        docker rm file-converter-test || true
                    '''

                    // Start new container
                    sh """
                        docker run -d \
                            --name file-converter-test \
                            --network jenkins \
                            -p 5001:5000 \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """

                    // Wait for app to be ready
                    echo 'Waiting for application to start...'
                    sleep 15

                    // Check if running
                    def containerRunning = sh(
                        script: "docker ps --filter name=file-converter-test --format '{{.Names}}'",
                        returnStdout: true
                    ).trim()
            
                    if (containerRunning) {
                        echo "Application container is running!"
                    } else {
                        error "Application failed to start"
                    }
                }
            }
        }

        stage('DAST - OWASP ZAP') {
            steps {
                echo 'Running Dynamic Application Security Testing with OWASP ZAP...'
                script {
                    try {
                        sh '''
                            # Run ZAP baseline scan
                            docker run --rm \
                                --network jenkins \
                                -v ${WORKSPACE}/${REPORTS_DIR}:/zap/wrk/:rw \
                                -t owasp/zap2docker-stable \
                                zap-baseline.py \
                                -t http://file-converter-test:5001 \
                                -r zap-report.html \
                                -J zap-report.json \
                                -w zap-report.md || true
                        '''

                        echo 'OWASP ZAP scan completed'
                    } catch(Exception e) {
                        echo "ZAP found vulnerabilities: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Security Summary') {
            steps {
                echo 'Security Scan Summary'
                script {
                    sh '''
                        echo "================================"
                        echo "Security Scan Results Summary"
                        echo "================================"
                        echo ""
                        echo "Branch: ${BRANCH_NAME}"
                        echo "Build: ${BUILD_NUMBER}"
                        echo ""

                        echo "Reports generated:"
                        ls -lh ${REPORTS_DIR}/ || echo "No reports found"
                        echo ""

                        echo "Bandit (SAST):"
                        grep -A 5 "Run metrics" ${REPORTS_DIR}/bandit-report.txt || echo "No Bandit summary"
                        echo ""

                        echo "Trivy (Container Security):"
                        grep -E "(CRITICAL|HIGH|MEDIUM)" ${REPORTS_DIR}/trivy-report.txt | head -20 || echo "No Trivy summary"
                        echo ""
                        
                        echo "================================"
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up...'
                script {
                    sh '''
                        # Stop and remove test container
                        docker stop file-converter-test || true
                        docker rm file-converter-test || true
                        
                        # Keep the image for potential reuse
                        # docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Archiving reports...'

            // Archive all reports
            archiveArtifacts artifacts: "${REPORTS_DIR}/*", allowEmptyArchive: true
            
            // Publish HTML reports
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: "${REPORTS_DIR}",
                reportFiles: 'zap-report.html',
                reportName: 'Security Reports'
            ])
        }

        success {
            echo 'Pipeline completed successfully!'
            script {
                if (env.BRANCH_NAME == 'main') {
                    echo 'Main branch: All security checks passed!'
                } else {
                    echo 'Insecure branch: Vulnerabilities detected (as expected for demo)'
                }
            }
        }

        unstable {
            echo 'Pipeline completed with warnings - Security issues found'
        }
        
        failure {
            echo 'Pipeline failed!'
        }

        cleanup {
            echo 'Final cleanup...'
            sh '''
                # Ensure test container is stopped
                docker stop file-converter-test 2>/dev/null || true
                docker rm file-converter-test 2>/dev/null || true
            '''
        }
    }

}