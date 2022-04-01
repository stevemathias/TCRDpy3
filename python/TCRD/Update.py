'''
Update methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2022-04-01 12:20:33 smathias>
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
    
  def do_update(self, init):
    '''
    Function  : Set a single table.col to val by row id
    Arguments : A dictionary with keys table, id, col and val
    Returns   : Boolean indicating success or failure
    '''
    if 'table' in init and 'id' in init and 'col' in init and 'val' in init:
      params = [init['val'], init['id']]
    else:
      self.warning(f"Invalid parameters sent to do_update(): {init}")
      return False
    sql = "UPDATE {} SET {} = %s WHERE id = %s".format(init['table'], init['col'])
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in do_update(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    return True

  def upd_tdls_null(self):
    '''
    Function  : Set all target.tdl values to NULL
    Arguments : N/A
    Returns   : Integer count of rows updated
    '''
    sql = "UPDATE target SET tdl = NULL"
    self._logger.debug(f"SQL: {sql}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql)
        row_ct = curs.rowcount
        self._conn.commit()
      except Error as e:
<<<<<<< HEAD
        self._logger.error(f"MySQL Error in upd_tdls_null(): {e}")
=======
        self._logger.error(f"MySQL Error in set_tdls_null(): {e}")
>>>>>>> 7a2d909d09fb375558f5724be512a09f5e4e59b7
        self._conn.rollback()
        return False
    return row_ct

  def upd_pmstdlis_zero(self):
    '''
<<<<<<< HEAD
    Function  : Set all JensenLab PubMed Score' tdl_info values to 0
=======
    Function  : Set all target.tdl values to NULL
>>>>>>> 7a2d909d09fb375558f5724be512a09f5e4e59b7
    Arguments : N/A
    Returns   : Integer count of rows updated
    '''
    sql = "UPDATE tdl_info SET number_value = 0 WHERE itype = 'JensenLab PubMed Score'"
    self._logger.debug(f"SQL: {sql}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql)
        row_ct = curs.rowcount
        self._conn.commit()
      except Error as e:
<<<<<<< HEAD
        self._logger.error(f"MySQL Error in upd_pmstdlis_zero(): {e}")
=======
        self._logger.error(f"MySQL Error in set_tdls_null(): {e}")
>>>>>>> 7a2d909d09fb375558f5724be512a09f5e4e59b7
        self._conn.rollback()
        return False
    return row_ct

<<<<<<< HEAD
  def upd_pms_tdlinfo(self, protein_id, number_value):
    '''
    Function  : Update a 'JensenLab PubMed Score' tdl_info value for a single protein_id
    Arguments : A protein_id and a number_value
    Returns   : Boolean indicating success or failure
    '''
    if protein_id and number_value:
      params = (number_value, protein_id)
    else:
      self.warning(f"Invalid parameters sent to upd_pms_tdlinfo()")
      return False
    sql = "UPDATE tdl_info SET number_value = %s WHERE protein_id = %s AND itype = 'JensenLab PubMed Score'"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in upd_pms_tdlinfo(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    return True

=======
  
>>>>>>> 7a2d909d09fb375558f5724be512a09f5e4e59b7
