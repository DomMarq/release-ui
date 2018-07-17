"""UI Server, Connects all Components."""
import os
from airflow_connector import AirflowDB
from airflow_adapter import AirflowAdapter
from flask import Flask
from flask import make_response
from flask_restful import Api
import resources

# creating the Flask application
APP = Flask(__name__)
API = Api(APP)


if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
  # Connect using the unix socket located at
  # /cloudsql/cloudsql-connection-name.
  cloudsql_unix_socket = os.path.join(
    '/cloudsql', os.environ.get('CLOUDSQL_INSTANCE_CONNECTION_NAME'))
  airflow_db = AirflowDB(unix_socket=cloudsql_unix_socket,
                         host=os.environ.get('CLOUDSQL_HOST'),
                         user=os.environ.get('CLOUDSQL_USER'),
                         password=os.environ.get('CLOUDSQL_PASSWORD'),
                         db=os.environ.get('CLOUDSQL_DB'))
else:
  airflow_db = AirflowDB(host=os.environ.get('CLOUDSQL_HOST'),
                         user=os.environ.get('CLOUDSQL_USER'),
                         password=os.environ.get('CLOUDSQL_PASSWORD'),
                         db=os.environ.get('CLOUDSQL_DB'))
adapter = AirflowAdapter(airflow_db)

# adding resource endpoints to different urls
API.add_resource(resources.Releases, '/releases', resource_class_kwargs={'adapter': adapter})
API.add_resource(resources.Release, '/release', resource_class_kwargs={'adapter': adapter})
API.add_resource(resources.Branches, '/branches', resource_class_kwargs={'adapter': adapter})
API.add_resource(resources.Types, '/types', resource_class_kwargs={'adapter': adapter})
API.add_resource(resources.Tasks, '/tasks', resource_class_kwargs={'adapter': adapter})
API.add_resource(resources.AirflowDBTesting, '/airflowdb', resource_class_kwargs={'airflow_db': adapter})  # TODO(dommarques): Delete when done

if __name__ == '__main__':
  APP.run(port='8080', debug=True)


# route to the first page
@APP.route('/')
def basic_pages():
  """Serves Webpage."""
  return make_response(open('templates/index.html').read())
