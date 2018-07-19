"""The Airflow Adapter."""
from datetime import datetime
from adapter_abc import Adapter
from filter_releases import filter_releases
from filter_releases import sort
from from_sql import read_releases
from from_sql import read_tasks
from to_sql import to_sql_release
from to_sql import to_sql_releases
from to_sql import to_sql_task
from to_sql import to_sql_tasks


class AirflowAdapter(Adapter):
  """Provides a way to interact with the Airflow Database, and get data from it."""

  def __init__(self, airflow_db):
    self._airflow_db = airflow_db

    raw_release_data = self._airflow_db.query('SELECT * FROM dag_run;')
    self._releases = read_releases(raw_release_data, self._airflow_db)

    branches = set()
    for release in self._releases:
      branches.add(self._releases[release].branch)
    self._branches = list(branches)

    types = set()
    for release in self._releases:
      types.add(self._releases[release].release_type)
    self._types = list(types)

  def get_releases(self, filter_options):
    # build the SQL query
    release_query = to_sql_releases(filter_options)
    # get the data from SQL
    release_data = self._airflow_db.query(release_query)
    # package the data into release objects with all neccessary info
    releases_data = read_releases(release_data, self._airflow_db)
    # filter for the stuff that SQL can't natively filter for,
    # due to some data being based on a tasks
    releases_data = filter_releases(releases_data, filter_options)
    # sort with the stuff that SQL can't natively sort according to,
    # due to some data being based on tasks
    releases_data = sort(releases_data, filter_options)

    return releases_data

  def get_release(self, release_name):
    # construct SQL query
    release_query = to_sql_release(release_name)
    # get data from SQL
    release_data = self._airflow_db.query(release_query)
    # package data into a release object
    release_data = read_releases(release_data, self._airflow_db)

    return release_data

  def get_tasks(self, execution_date):
    """Retrieve all task information.

    Args:
      execution_date: unix format

    Returns:
      Dictionary of Task objects.
    """
    # build SQl query
    task_query = to_sql_tasks(execution_date)
    # get data from SQL
    task_data = self._airflow_db.query(task_query)
    # package data into task objects
    task_objects = read_tasks(task_data)

    return task_objects

  def get_task(self, task_name, execution_date):
    task_query = to_sql_task(task_name, execution_date)
    task_data = self._airflow_db.query(task_query)
    task_data = read_tasks(task_data)

    return task_data

  def get_labels(self):
    """Retrieve all possible labels for UI.

    Returns:
      Array of labels as strings.
    """
    pass

  def get_branches(self):
    """Retrieve all possible branches for UI.

    Returns:
      Array of branches as strings.
    """
    # check if cache is older than 30 mins. If true, then update cache
    if (self._cache_last_updated - datetime.now()).total_seconds() > 1800:
      self.update_cache()
    return self._branches

  def get_release_types(self):
    """Retrieve all possible types for UI.

    Returns:
      Array of types as strings.
    """
    return self._types

  def update_cache(self):
    raw_release_data = self._airflow_db.query('SELECT * FROM dag_run;')
    self._releases = read_releases(raw_release_data, self._airflow_db)

    branches = set()
    for release in self._releases:
      branches.add(self._releases[release].branch)
    self._branches = list(branches)

    types = set()
    for release in self._releases:
      types.add(self._releases[release].release_type)
    self._types = list(types)

    self._cache_last_updated = datetime.now()
