'''
Update methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2020-12-08 12:56:29 smathias>
'''
from mysql.connector import Error
from contextlib import closing

class UpdateMethodsMixin:

  def upd_dataset_by_name(self, name, updates):
    colsvals = []
    params = []
    for col,val in updates.items():
      colsvals.append(f"{col} = %s")
      params.append(val)
    sql = "UPDATE dataset SET {} WHERE name = %s".format( ', '.join(colsvals))
    params.append(name)
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in upd_dataset_by_name(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    return True
    
