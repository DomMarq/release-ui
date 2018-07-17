"""REST API."""
import json
from filter_releases import filter_releases
from filter_releases import sort
from flask_restful import reqparse
from flask_restful import Resource
from to_timestamp import to_timestamp
release_requests = {}


def in_cache(args):
  """Checks if request arguments are in cache."""

  # parse args into different parameters
  start_date = hex(int(args['start_date']))
  end_date = hex(int(args['end_date']))
  datetype = str(args['datetype'])
  state = str(int(args['state']))
  branch = str(args['branch'])
  release_type = str(args['release_type'])
  sort_method = str(int(args['sort_method']))
  reverse = str(args['descending'])

  # create an autogenerated key for cache
  key = start_date + end_date + datetype + state + branch + release_type + sort_method + reverse

  # check if key has already been requested
  if key in release_requests:
    return key, release_requests[key]
  else:
    return False, key


def to_json(objects):
  """Turns list of objects (tasks or releases) to json."""
  output = []
  for item in objects:
    output.append(item.to_json())
  return json.dumps(output)


class Releases(Resource):
  """"Resource for all releases GET request."""

  def __init__(self, adapter):
    self._adapter = adapter

  def get(self):
    # parse the post request for the requisite info
    parser = reqparse.RequestParser()
    parser.add_argument('start_date')
    parser.add_argument('end_date')
    parser.add_argument('datetype')
    parser.add_argument('state')
    parser.add_argument('branch')
    parser.add_argument('release_type')
    parser.add_argument('sort_method')
    parser.add_argument('limit')
    parser.add_argument('offset')
    parser.add_argument('descending')
    args = parser.parse_args()

    # check if limit and offset exist, if not provide defaults
    if not args['limit']:
      args['limit'] = 100
    if not args['offset']:
      args['offset'] = 0

    # define start and end of desired array section
    array_from = int(args['offset'])
    array_to = int(args['limit'])+int(args['offset'])

    # # checks if the filtered, sorted data is already in memcache
    # cache_exists, cache_results = in_cache(args)
    # if cache_exists:
    #   return to_json(cache_results[array_from:array_to])
    # else:
    #   # filter and sort all releases with given parsed arguments
    #   response = filter_releases(self._adapter.get_releases(), args['state'], args['branch'], args['release_type'], args['start_date'], args['end_date'], args['datetype'])
    #   response = sort(response, args['sort_method'], args['descending'])
    #   release_requests[cache_results] = response

    response = self._adapter.get_releases(start_date=float(args['start_date']),
                                    end_date=float(args['end_date']),
                                    datetype=str(args['datetype']),
                                    state=int(args['state']),
                                    branch=str(args['branch']),
                                    release_type=str(args['release_type']),
                                    sort_method=int(args['sort_method']),
                                    descending=int(args['descending']))

      # returns a jsonified array with the determined start and end indices
    return to_json(response[array_from:array_to])


class Release(Resource):
  """"Resource for single release GET request."""

  def __init__(self, adapter):
    self._adapter = adapter

  def get(self):
    parser = reqparse.RequestParser()
    parser.add_argument('release')
    args = parser.parse_args()
    response = self._adapter.get_release(str(args['release']))
    response = to_json([response[str(args['release'])]])
    return response


class Branches(Resource):
  """"Resource for Branches GET request."""

  def __init__(self, adapter):
    self._adapter = adapter

  def get(self):
    return json.dumps(self._adapter.get_branches())


class Types(Resource):
  """"Resource for types GET request."""

  def __init__(self, adapter):
    self._adapter = adapter

  def get(self):
    return json.dumps(self._adapter.get_types())


class Tasks(Resource):
  """"Resource for tasks GET request."""

  def __init__(self, adapter):
    self._adapter = adapter

  def get(self):
    parser = reqparse.RequestParser()
    parser.add_argument('release')
    args = parser.parse_args()

    release = self._adapter.get_release(str(args['release']))
    release_tasks = release[str(args['release'])].tasks
    execution_date = to_timestamp(release[str(args['release'])].started)
    task_objects = []
    for task_id in release_tasks:
      task_object = self._adapter.get_task(task_id, execution_date)
      # if type(task_object) == 'list':
      task_object = task_object[0]
      task_objects.append(task_object)
    response = to_json(task_objects)
    return response


class AirflowDBTesting(Resource):  # TODO(dommarques): delete when done with it
  """Allows for SQL queries to be sent to App Engine through an HTTP GET request. FOR TESTING ONLY, WILL BE DELETED."""  # pylint: disable=line-too-long

  def __init__(self, airflow_db):
    self._airflow_db = airflow_db

  def get(self):
    parser = reqparse.RequestParser()
    parser.add_argument('cm')
    parser.add_argument('start_date')
    parser.add_argument('end_date')
    parser.add_argument('datetype')
    parser.add_argument('state')
    parser.add_argument('label')
    parser.add_argument('sort_method')
    parser.add_argument('limit')
    parser.add_argument('offset')
    args = parser.parse_args()
    data = self._airflow_db.query(str(args['cm']))
