
pipeline {
    agent {
        docker {
            image 'dalred/todoapp:main-version-2972219117'
            args '--network todoapp_mynetwork -e DB_HOST=db -e POSTGRES_PASSWORD=djangoappuserdb -e POSTGRES_PORT=5432 -e POSTGRES_USER=djangoappuserdb -e POSTGRES_DB=djangoappuserdb'
        }
    }
    environment {
        TEST_RUN_ID = "$TEST_RUN_ID"
        URL_TESTIT = "$URL_TESTIT"
        PRIVATE_TOKEN = "$PRIVATE_TOKEN_TESTIT"
        CONFIGURATIONID = "$CONFIGURATIONID_TESTIT"

    }
    stages {
        stage('git') {
            steps {
                git branch: 'main', url:'https://github.com/dalred/ToDoApp.git'
            }
        }
        stage('tests') {
            steps {
                sh "cd myappcalendar && pytest tests/users/ tests/goals/ -vv --testit --testrunid $TEST_RUN_ID --testit_url $URL_TESTIT --privatetoken $PRIVATE_TOKEN --configurationid $CONFIGURATIONID"
            }
        }
    }
    post { // после всей сборки
      cleanup {
          cleanWs()
      }
  }
}



