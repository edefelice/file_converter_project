pipeline {
    agent any

    //parameters {
    //    booleanParam {
    //        name: 'PUSH_TO_DOCKERHUB',
    //        defaultValue: false,
    //        description: 'Push Docker image to Docker Hub (only for main branch with clean scans)'
    //    }
    //}

    environment {
        // Project configuration
        PROJECT_NAME = 'file_converter_project'
        DOCKER_IMAGE = 'file-converter'
        DOCKER_TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"

        // Snyk credentials
        SNYK_TOKEN = credentials('snyk-token')

        // Docker Hub credentials
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')

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
                    python3 --version
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
                            pip3 install bandit
                            bandit -r app/ -f json -o ${REPORTS_DIR}/bandit-report.json || true
                            bandit -r app/ -f html -o ${REPORTS_DIR}/bandit-report.html || true
                            bandit -r app/ -f txt -o ${REPORTS_DIR}/bandit-report.txt || true
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
                        snykSecurity(
                            snykInstallation: 'snyk',
                            snykTokenId: 'snyk-token',
                            projectName: "${PROJECT_NAME}",
                            failOnIssues: false,
                            severity: 'low'
                        )

                        echo 'Snyk scan completed'
                    } catch(Exception e) {
                        echo "Snyk found vulnerabilities: ${e.message}"
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
                        docker tag ${DOCKER_IMAGE}::${DOCKER_TAG} ${DOCKER_IMAGE}:latest
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
                    // Stop any existing container
                    sh '''
                        docker stop file-converter-test || true
                        docker rm file-converter-test || true
                    '''

                    // Start new container
                    sh '''
                        docker run -d \
                            --name file-converter-test \
                            --network jenkins \
                            -p 5001:5000 \
                            ${DOCKER_IMAGE}:{DOCKER_TAG}
                    '''

                    // Wait for app to be ready
                    sh '''
                        echo "Waiting for application to start..."
                        sleep 10

                        # Check if app is responding
                        for i in {1..10}; do
                            if curl -f http://localhost:5001/ > /dev/null 2>&1; then
                            echo "Application is ready!"
                            exit 0
                            fi
                            echo "Waiting... attempt $i/10"
                            sleep 3
                        done

                        echo "Application failed to start"
                        docker logs file-converter-test
                        exit 1
                    '''
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

        //stage('Push to Docker Hub') {
        //    when {
        //        allOf {
        //            branch 'main'
        //            expression { return params.PUSH_TO_DOCKERHUB }
        //        }
        //    }

        //    steps {
        //        echo 'Pushing Docker image to Docker Hub...'
        //        script {
        //            sh '''
        //                echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin

        //                # Tag for Docker Hub
        //                docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE}:latest
        //                docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE}:${DOCKER_TAG}

        //                # Push
        //                docker push ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE}:latest
        //                docker push ${DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        
        //                docker logout
        //            '''
        //            echo "Image pushed to Docker Hub: ${env.DOCKERHUB_CREDENTIALS_USR}/${DOCKER_IMAGE}"
        //        }
        //    }
        //}

        stage('Cleanup') {
            steps {
                echo '🧹 Cleaning up...'
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
                reportFiles: 'bandit-report.html,zap-report.html',
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