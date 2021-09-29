'''
Delete methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2021-04-27 15:14:29 smathias>
'''
from mysql.connector import Error
from contextlib import closing

class DeleteMethodsMixin:

  def del_all_rows(self, table_name):
    if not table_name:
      self.warning("No table name sent to del_all_rows()")
      return False
    dsql = f"DELETE FROM {table_name}"
    asql = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(dsql)
        row_ct = curs.rowcount
        curs.execute(asql)
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in del_all_rows() for table {table_name}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_dataset(self, name):
    if not name:
      self.warning("No dataset name sent to del_dataset()")
      return False
    psql = "DELETE FROM provenance WHERE dataset_id = (SELECT id FROM dataset WHERE name = %s)"
    dsql = "DELETE FROM dataset WHERE name = %s"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(psql, (name,))
        #prov_ct = curs.rowcount
        curs.execute(dsql, (name,))
        #ds_ct = curs.rowcount
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in del_dataset() for '{name}': {e}")
        self._conn.rollback()
        return False
    return True
             
  def del_tdl_infos(self, itype):
    if not itype:
      self.warning("No itype sent to del_tdl_infos()")
      return False
    sql = f"DELETE FROM tdl_info WHERE itype = %s"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, (itype,))
        self._conn.commit()
        row_ct = curs.rowcount
      except Error as e:
        self._logger.error(f"MySQL Error in del_tdl_infos() for itype {itype}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_cmpd_activities(self, catype):
    if not catype:
      self.warning("No catype sent to del_cmpd_activities()")
      return False
    sql = f"DELETE FROM cmpd_activity WHERE catype = %s"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, (catype,))
        self._conn.commit()
        row_ct = curs.rowcount
      except Error as e:
        self._logger.error(f"MySQL Error in del_cmpd_activities() for catype {catype}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_diseases(self, dtype):
    if not dtype:
      self.warning("No dtype sent to del_diseases()")
      return False
    if dtype == 'DISEASES':
      sql = "DELETE FROM disease WHERE dtype LIKE 'JensenLab%'"
    else:
      sql = f"DELETE FROM disease WHERE dtype = {dtype}"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql)
        row_ct = curs.rowcount
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in del_diseases() for dtype {dtype}: {e}")
        self._conn.rollback()
        return False
    return row_ct

