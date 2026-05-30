pipeline {
  agent {
    docker {
      image 'python:3.11'
      args '--user root --network jenkins-network -v /opt/spark-libs:/opt/spark-libs'
    }
  }

  environment {
    MYSQL_HOST = 'mysql-db'
    MYSQL_PORT = '3306'
    MYSQL_DB   = 'salesdb'
    MYSQL_USER = 'jenkins'
    MYSQL_PASS = 'jenkins123'
    JAVA_HOME  = '/usr/lib/jvm/java-17-openjdk-amd64'
  }

  stages {
    stage('Install Dependencies') {
      steps {
        echo 'Installing Java and PySpark...'
        sh '''
          apt-get update -q
          apt-get install -y -q default-jdk
          pip install -r requirements.txt --quiet
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
      }
    }

    stage('Test MySQL Connection') {
      steps {
        echo 'Checking MySQL is reachable...'
        sh '''
          apt-get install -y -q default-mysql-client
          mysql -h mysql-db -u jenkins -pjenkins123 salesdb -e "SELECT COUNT(*) as total_rows FROM sales;"
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
