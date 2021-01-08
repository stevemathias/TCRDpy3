'''
Create (ie. INSERT) methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2020-12-11 11:02:22 smathias>
'''
from mysql.connector import Error
from contextlib import closing

class CreateMethodsMixin:
  
  def ins_dataset(self, init):
    if 'name' in init and 'source' in init :
      params = [init['name'], init['source']]
    else:
      self.warning("Invalid parameters sent to ins_dataset(): ", init)
      return False
    cols = ['name', 'source']
    vals = ['%s','%s']
    for optcol in ['app', 'app_version', 'datetime', 'url', 'comments']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO dataset (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        dataset_id = curs.lastrowid
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in ins_dataset(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    return dataset_id

  def ins_provenance(self, init):
    if 'dataset_id' in init and 'table_name' in init :
      params = [init['dataset_id'], init['table_name']]
    else:
      self.warning("Invalid parameters sent to ins_provenance(): ", init)
      return False
    cols = ['dataset_id', 'table_name']
    vals = ['%s','%s']
    for optcol in ['column_name', 'where_clause', 'comment']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO provenance (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL Error in ins_provenance(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    return True
  
  def ins_drgc_resource(self, init, commit=True):
    if 'rssid' in init and 'resource_type' in init and 'target_id' in init and 'json' in init:
      cols = ['rssid', 'resource_type', 'target_id', 'json']
      vals = ['%s','%s','%s','%s']
      params = [init['rssid'], init['resource_type'], init['target_id'], init['json']]
    else:
      self.warning("Invalid parameters sent to ins_drgc_resource(): ", init)
      return False
    sql = "INSERT INTO drgc_resource ({}) VALUES ({})".format(','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_drgc_resource(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_drgc_resource(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_pmscore(self, init, commit=True):
    if 'protein_id' in init and 'year' in init and 'score' in init:
      params = [init['protein_id'], init['year'], init['score']]
    else:
      self.warning(f"Invalid parameters sent to ins_pmscore(): {init}")
      return False
    sql = "INSERT INTO pmscore (protein_id, year, score) VALUES (%s, %s, %s)"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_pmscore(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_pmscore(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_disease(self, init, commit=True):
    if 'dtype' in init and 'name' in init:
      cols = ['dtype', 'name']
      params = [init['dtype'], init['name']]
    else:
      self.warning("Invalid parameters sent to ins_disease(): ", init)
      return False
    if 'protein_id' in init:
      cols.insert(0, 'protein_id')
      vals = ['%s','%s','%s']
      params.insert(0, init['protein_id'])
    elif 'nhprotein_id' in init:
      cols.insert(0, 'nhprotein_id')
      vals = ['%s','%s','%s']
      params.insert(0, init['nhprotein_id'])
    else:
      self.warning(f"Invalid parameters sent to ins_disease(): {init}")
      return False
    for optcol in ['did', 'evidence', 'zscore', 'conf', 'description', 'reference', 'drug_name', 'log2foldchange', 'pvalue', 'score', 'source', 'O2s', 'S2O']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO disease (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_disease(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_disease(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_tinx_novelty(self, init, commit=True):
    if 'protein_id' in init and 'score' in init:
      params = [init['protein_id'], init['score']]
    else:
      self.warning(f"Invalid parameters sent to ins_tinx_novelty(): {init}")
      return False
    sql = "INSERT INTO tinx_novelty (protein_id, score) VALUES (%s, %s)"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_tinx_novelty(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_tinx_novelty(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_tinx_disease(self, init, commit=True):
    if 'doid' in init and 'name' in init:
      params = [init['doid'], init['name']]
    else:
      self.warning(f"Invalid parameters sent to ins_tinx_disease(): {init}")
      return False
    cols = ['doid', 'name']
    vals = ['%s','%s']
    for optcol in ['parent_doid', 'num_children', 'summary', 'num_important_targets', 'score']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO tinx_disease (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_tinx_disease(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_tinx_disease(): {e}")
        self._conn.rollback()
        return False
    return True
    
  def ins_tinx_importance(self, init, commit=True):
    if 'protein_id' in init and 'disease_id' in init and 'score' in init:
      params = [init['protein_id'], init['disease_id'], init['score']]
    else:
      self.warning(f"Invalid parameters sent to ins_tinx_importance(): {init}")
      return False
    sql = "INSERT INTO tinx_importance (protein_id, disease_id, score) VALUES (%s, %s, %s)"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        iid = curs.lastrowid
      except Error as e:
        self._logger.error(f"MySQL Error in ins_tinx_importance(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_tinx_importance(): {e}")
        self._conn.rollback()
        return False
    return iid
    
  def ins_tinx_articlerank(self, init, commit=True):
    if 'importance_id' in init and 'pmid' in init and 'rank' in init:
      params = [init['importance_id'], init['pmid'], init['rank']]
    else:
      self.warning(f"Invalid parameters sent to ins_tinx_articlerank(): {init}")
      return False
    sql = "INSERT INTO tinx_articlerank (importance_id, pmid, rank) VALUES (%s, %s, %s)"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        iid = curs.lastrowid
      except Error as e:
        self._logger.error(f"MySQL Error in ins_tinx_articlerank(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_tinx_articlerank(): {e}")
        self._conn.rollback()
        return False
    return True
  
