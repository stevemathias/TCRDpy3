'''
Delete methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2020-12-11 10:07:57 smathias>
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
        curs.execute(asql)
        self._conn.commit()
        row_ct = curs.rowcount()
      except Error as e:
        self._logger.error(f"MySQL Error in del_all_rows() for table {table_name}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_tdl_infos(self, itype):
    if not itype:
      self.warning("No itype sent to del_tdl_infos()")
      return False
    sql = f"DELETE FROM tdl_info WHERE itype = %s"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, (itype,))
        self._conn.commit()
        row_ct = curs.rowcount()
      except Error as e:
        self._logger.error(f"MySQL Error in del_tdl_infos() for itype {itype}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_diseases(self, dtype):
    if not dtype:
      self.warning("No dtype sent to del_diseases()")
      return False
    sql = f"DELETE FROM diseases WHERE dtype = %s"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, (dtype,))
        self._conn.commit()
        row_ct = curs.rowcount()
      except Error as e:
        self._logger.error(f"MySQL Error in del_diseases() for dtype {dtype}: {e}")
        self._conn.rollback()
        return False
    return row_ct

  def del_jldiseases(self):
    sql = f"DELETE FROM diseases WHERE dtype like 'JensenLab%'"
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql)
        self._conn.commit()
        row_ct = curs.rowcount()
      except Error as e:
        self._logger.error(f"MySQL Error in del_jldiseases(): {e}")
        self._conn.rollback()
        return False
    return row_ct
