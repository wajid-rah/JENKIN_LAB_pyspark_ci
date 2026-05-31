pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '--user root --network jenkins-network -v /opt/spark-libs:/opt/spark-libs'

            // docker run python:3.11 \
            //     --user root \
            //     --network jenkins-network \  // Connect pyspark/jenkins container to the same docker network (mysql running)
            //     -v /opt/spark-libs:/opt/spark-libs

            /*
            jenkins-network
            ─────────────────────────────────────────
              mysql-db container    python:3.11 container
              (MySQL running)   ←── (PySpark job running)
            ─────────────────────────────────────────

            Mount
            host machine                    python:3.11 container
            (Jenkins downloaded and stored)
            /opt/spark-libs/          →     /opt/spark-libs/
              mysql-connector.jar             mysql-connector.jar  ✅
            */
        }
    }

    environment {
        MYSQL_HOST = 'mysql-db'
        MYSQL_PORT = '3306'
        MYSQL_DB   = 'salesdb'
        MYSQL_USER = 'user'
        MYSQL_PASS = 'root'
        JAVA_HOME  = '/usr/lib/jvm/java-17-openjdk-amd64'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                echo 'Installing Java and PySpark...'
                sh '''
                    apt-get update -q
                    apt-get install -y default-jdk   # needs root ✅
                    pip install -r requirements.txt  # needs root ✅
                '''
            }
        }

        stage('Download MySQL Driver') {
            steps {
                echo 'Downloading MySQL JDBC driver...'
                sh '''
                    mkdir -p /opt/spark-libs
                    if [ ! -f /opt/spark-libs/mysql-connector.jar ]; then
                        curl -L -o /opt/spark-libs/mysql-connector.jar \
                        https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.33/mysql-connector-java-8.0.33.jar
                        echo "Driver downloaded!"
                    else
                        echo "Driver already exists, skipping download."
                    fi
                '''

                // if the file does NOT exist → run the download
                // Part                              Meaning
                // if [ ]                            standard shell if condition
                // !                                 NOT — reverses the result
                // -f                                check if this is a regular file
                // /opt/spark-libs/mysql-connector.jar   the file to check
                // fi  ← always required to close the if block
            }
        }

        stage('Test MySQL Connection') {
            steps {
                echo 'Checking MySQL is reachable...'
                sh '''
                    apt-get install -y -q default-mysql-client
                    mysql -h mysql-db -u root -proot --skip-ssl salesdb -e "SELECT COUNT(*) as total_rows FROM sales;"
                     # MySQL 8.0 enables SSL by default. When the mysql client tries to connect, it sees a self-signed certificate 
                     # and refuses it as untrusted. Since this is a local dev/learning setup, we can just disable SSL.
                     
                '''
            }
        }

        stage('Run PySpark Job') {
            steps {
                echo 'Running PySpark job...'
                sh 'python3 spark_job.py'
            }
        }
    }

    post {
        success { echo 'PySpark job completed — data read successfully!' }
        failure { echo 'Job failed — check logs above.' }
        always  { echo 'Pipeline finished.' }
    }
}
