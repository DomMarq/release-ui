"""Converts the request arguments to a SQL query."""
import datetime
from resources.dag_name_parser import dag_name_parser
from data.state import State


def to_sql_releases(filter_options):
  """Converts a set of parameters contained in 'args' to a SQL query.

  Gets the releases(AKA dag runs) which fit the parameters.

  Args:
    filter_options: object with filtering parameters

  Returns:
    sql_query: a string which is dynamically constructed using all of the params
  """
  sql_query = 'SELECT dag_id, execution_date FROM dag_run'
  # convert start and end date from unix to python datetime
  start_date = datetime.datetime.fromtimestamp(filter_options.start_date)
  end_date = datetime.datetime.fromtimestamp(filter_options.end_date)
  # append the date filter to the query based on:
  # datetype, start_date, and end_date
  if filter_options.datetype == 0:
    sql_query += ' WHERE execution_date BETWEEN "' + str(start_date) + '" AND "'+ str(end_date) + '"'  # pylint: disable=line-too-long
  else:
    sql_query += ' WHERE execution_date BETWEEN "' + str(start_date) + '" AND "'+ str(end_date) + '"'  # pylint: disable=line-too-long
  # append a state filter, if there is one available -- '0' means all states
  if filter_options.state != 0:
    sql_query += ' AND state = "%s"' %(convert_state(state))
  # add sorting parameter
  sql_query = add_sorting(sql_query, filter_options.sort_method, filter_options.reverse)
  # TODO(dommarques) - add label filtering, probably just the dag_id
  sql_query += ';'   # put the finishing touch on it
  return sql_query


def to_sql_release(release_id):
  # get id and execution date from release id
  dag_id, execution_date = dag_name_parser(release_id)
  # construct query
  sql_query = 'SELECT dag_id, execution_date FROM dag_run'
  sql_query += ' WHERE dag_id = "' + dag_id + '"'
  sql_query += ' AND execution_date = "' + str(execution_date) + '"'
  sql_query += ';'   # put the finishing touch on it
  return sql_query


def to_sql_tasks(execution_date):
  sql_query = 'SELECT task_id, dag_id, execution_date, start_date, end_date, state FROM task_instance'
  sql_query += ' WHERE execution_date = "' + str(datetime.datetime.fromtimestamp(execution_date)) + '"'
  sql_query += ' ORDER BY execution_date DESC'
  sql_query += ';'   # put the finishing touch on it
  return sql_query


def to_sql_task(task_name, execution_date):
  sql_query = 'SELECT task_id, dag_id, execution_date, start_date, end_date, state FROM task_instance'
  sql_query += ' WHERE execution_date = "' + str(datetime.datetime.fromtimestamp(execution_date)) + '"'
  sql_query += ' AND task_id = "' + task_name + '"'
  sql_query += ' ORDER BY execution_date DESC'
  sql_query += ';'   # put the finishing touch on it
  return sql_query


def to_sql_xcom(dag_id, execution_date):
  sql_query = 'SELECT value FROM xcom'
  sql_query += ' WHERE execution_date = "' + str(datetime.datetime.fromtimestamp(execution_date)) + '"'
  sql_query += ' AND dag_id = "' + dag_id + '"'
  sql_query += ';'
  return sql_query


def convert_state(state):
  """Converts the state enumeration into the format needed for the SQL query.

  Args:
    state: the integer which enumerates the requested state (int)

  Returns:
    state: string format which follows the same format in the SQl db (str)
  """
  state = int(state)
  if state == State.UNUSED_STATUS:
    return 'none'
  elif state == State.PENDING:
    return 'running'
  elif state == State.FINISHED:
    return 'success'
  elif state == State.FAILED:
    return 'failed'
  elif state == State.ABANDONED:
    return 'shutdown'


def add_sorting(sql_query, sort_method, reverse):
  """Adds sorting parameter to SQL query.

  Args:
    sql_query: the query so far, which will have sorting appended to end (str)
    sort_method: the sort method (int).
    reverse: boolean

  Returns:
    sql_query: now with sorting! (str)
  """
  if sort_method == 1:
    sql_query += ' ORDER BY run_id'
  elif sort_method == 2:
    sql_query += ' ORDER BY execution_date'
  elif sort_method > 2:
    # ensure that the non-relevant sort methods don't cause errors
    return sql_query
  if reverse:
    sql_query += ' DESC'
  else:
    sql_query += ' ASC'
  return sql_query
