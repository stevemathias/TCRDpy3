'''
Create (ie. INSERT) methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2021-01-19 13:36:12 smathias>
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
  
  def ins_target(self, init):
    '''
    Function  : Insert a target and all associated data provided.
    Arguments : Dictionary containing target data.
    Returns   : Integer containing target.id
    Example   : tid = dba->ins_target(init) ;
    Scope     : Public
    Comments  : This only handles data parsed from UniProt XML entries in load-UniProt.py
    '''
    if 'name' in init and 'ttype' in init:
      params = [init['name'], init['ttype']]
    else:
      self.warning(f"Invalid parameters sent to ins_target(): {init}")
      return False
    cols = ['name', 'ttype']
    vals = ['%s','%s']
    for optcol in ['description', 'comment']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO target (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    target_id = None
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        target_id = curs.lastrowid
      except Error as e:
        self._logger.error(f"MySQL Error in ins_target(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    for protein in init['components']['protein']:
      protein_id = self.ins_protein(protein, commit=False)
      if not protein_id:
        return False
      sql = "INSERT INTO t2tc (target_id, protein_id) VALUES (%s, %s)"
      params = (target_id, protein_id)
      self._logger.debug(f"SQLpat: {sql}")
      self._logger.debug(f"SQLparams: {params}")
      with closing(self._conn.cursor()) as curs:
        try:
          curs.execute(sql, tuple(params))
        except Error as e:
          self._logger.error(f"MySQL Error in ins_target(): {e}")
          self._logger.error(f"SQLpat: {sql}")
          self._logger.error(f"SQLparams: {params}")
          self._conn.rollback()
          return False
      try:
        self._conn.commit()
      except Error as e:
        self._conn.rollback()
        self._logger.error(f"MySQL commit error in ins_target(): {e}")
        return False
    return target_id

  def ins_protein(self, init, commit=True):
    '''
    Function  : Insert a protein and all associated data provided.
    Arguments : Dictionary containing target data.
    Returns   : Integer containing target.id
    Example   : pid = dba->ins_protein(init) ;
    Scope     : Public
    Comments  : This only handles data parsed from UniProt XML entries in load-UniProt.py
    '''
    if 'name' in init and 'description' in init and 'uniprot' in init:
      params = [init['name'], init['description'], init['uniprot']]
    else:
      self.warning(f"Invalid parameters sent to ins_protein(): {init}")
      return False
    cols = ['name', 'description', 'uniprot']
    vals = ['%s','%s', '%s']
    for optcol in ['up_version', 'geneid', 'sym', 'family', 'chr', 'seq']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO protein (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    protein_id = None
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        protein_id = curs.lastrowid
      except Error as e:
        self._logger.error(f"MySQL Error in ins_protein(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if 'aliases' in init:
      for d in init['aliases']:
        d['protein_id'] = protein_id
        rv = self.ins_alias(d, commit=False)
        if not rv:
          return False
    if 'xrefs' in init:
      for d in init['xrefs']:
        d['protein_id'] = protein_id
        rv = self.ins_xref(d, commit=False)
        if not rv:
          return False
    if 'tdl_infos' in init:
      for d in init['tdl_infos']:
        d['protein_id'] = protein_id
        rv = self.ins_tdl_info(d, commit=False)
        if not rv:
          return False
    if 'goas' in init:
      for d in init['goas']:
        d['protein_id'] = protein_id
        rv = self.ins_goa(d, commit=False)
        if not rv:
          return False
    if 'expressions' in init:
      for d in init['expressions']:
        d['protein_id'] = protein_id
        rv = self.ins_expression(d, commit=False)
        if not rv:
          return False
    if 'pathways' in init:
      for d in init['pathways']:
        d['protein_id'] = protein_id
        rv = self.ins_pathway(d, commit=False)
        if not rv:
          return False
    if 'diseases' in init:
      for d in init['diseases']:
        d['protein_id'] = protein_id
        rv = self.ins_disease(d, commit=False)
        if not rv:
          return False
    if 'features' in init:
      for d in init['features']:
        d['protein_id'] = protein_id
        rv = self.ins_feature(d, commit=False)
        if not rv:
          return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._conn.rollback()
        self._logger.error(f"MySQL commit error in ins_protein(): {e}")
        return False
    return protein_id

  def ins_nhprotein(self, init):
    if 'uniprot' in init and 'name' in init and 'species' in init and 'taxid' in init:
      params = [init['uniprot'], init['name'], init['species'], init['taxid']]
    else:
      self.warning(f"Invalid parameters sent to ins_nhprotein(): {init}")
      return False
    cols = ['uniprot', 'name', 'species', 'taxid']
    vals = ['%s','%s','%s','%s']
    for optcol in ['sym', 'description', 'geneid', 'stringid']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO nhprotein (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    nhprotein_id = None
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
        nhprotein_id = curs.lastrowid
      except Error as e:
        self._logger.error(f"MySQL Error in ins_nhprotein(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if 'xrefs' in init:
      for d in init['xrefs']:
        d['nhprotein_id'] = nhprotein_id
        rv = self.ins_xref(d, commit=False)
        if not rv:
          return False
    try:
      self._conn.commit()
    except Error as e:
      self._conn.rollback()
      self._logger.error(f"MySQL commit error in ins_nhprotein(): {e}")
      return False
    return nhprotein_id

  def ins_alias(self, init, commit=True):
    if 'protein_id' not in init or 'type' not in init or 'dataset_id' not in init or 'value' not in init:
      self.warning("Invalid parameters sent to ins_alias(): ", init)
      return False
    sql = "INSERT INTO alias (protein_id, type, dataset_id, value) VALUES (%s, %s, %s, %s)"
    params = (init['protein_id'], init['type'], init['dataset_id'], init['value'])
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
        self._logger.error(f"MySQL Error in ins_alias(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_alias(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_xref(self, init, commit=True):
    if 'xtype' in init and 'dataset_id' in init and 'value' in init:
      params = [init['xtype'], init['dataset_id'], init['value']]
    else:
      self.warning(f"Invalid parameters sent to ins_xref(): {init}")
      return False
    if 'protein_id' in init:
      cols = ['protein_id', 'xtype', 'dataset_id', 'value']
      vals = ['%s','%s','%s','%s']
      params.insert(0, init['protein_id'])
    elif 'target_id' in init:
      cols = ['target_id', 'xtype', 'dataset_id', 'value']
      vals = ['%s','%s','%s','%s']
      params.insert(0, init['target_id'])
    elif 'nhprotein_id' in init:
      cols = ['nhprotein_id', 'xtype', 'dataset_id', 'value']
      vals = ['%s','%s','%s','%s']
      params.insert(0, init['nhprotein_id'])
    else:
      self.warning("Invalid parameters sent to ins_xref(): ", init)
      return False
    if 'xtra' in init:
      cols.append('xtra')
      vals.append('%s')
      params.append(init['xtra'])
    sql = "INSERT INTO xref (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    protein_id = None
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
        pass
        # if 'Duplicate entry' in e[1] and "key 'xref_idx5'" in e[1]:
        #   pass
        # else:
        #   self._logger.error(f"MySQL Error in ins_xref(): {e}")
        #   self._logger.error(f"SQLpat: {sql}")
        #   self._logger.error(f"SQLparams: {params}")
        #   self._conn.rollback()
        #   return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_xref(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_tdl_info(self, init, commit=True):
    if 'itype' in init:
      itype = init['itype']
    else:
      self.warning(f"Invalid parameters sent to ins_tdl_info(): {init}")
      return False
    if 'string_value' in init:
      val_col = 'string_value'
      value = init['string_value']
    elif 'integer_value' in init:
      val_col = 'integer_value'
      value = init['integer_value']
    elif 'number_value' in init:
      val_col = 'number_value'
      value = init['number_value']
    elif 'boolean_value' in init:
      val_col = 'boolean_value'
      value = init['boolean_value']
    elif 'date_value' in init:
      val_col = 'date_value'
      value = init['date_value']
    else:
      self.warning(f"Invalid parameters sent to ins_tdl_info(): {init}")
      return False
    if 'protein_id' in init:
      xid = init['protein_id']
      sql = "INSERT INTO tdl_info (protein_id, itype, %s)" % val_col
    elif 'target_id' in init:
      xid = init['target_id']
      sql = "INSERT INTO tdl_info (target_id, itype, %s)" % val_col
    else:
      self.warning(f"Invalid parameters sent to ins_tdl_info(): {init}")
      return False
    sql += " VALUES (%s, %s, %s)"
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {xid}, {itype}, {value}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, (xid, itype, value))
      except Error as  e:
        self._logger.error(f"MySQL Error in ins_tdl_info(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {xid}, {itype}, {value}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_tdl_info(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_goa(self, init, commit=True):
    if 'protein_id' in init and 'go_id' in init:
      params = [init['protein_id'], init['go_id']]
    else:
      self.warning(f"Invalid parameters sent to ins_goa(): {init}")
      return False
    cols = ['protein_id', 'go_id']
    vals = ['%s','%s']
    for optcol in ['go_term', 'evidence', 'goeco', 'assigned_by']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO goa (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
         self._logger.error(f"MySQL Error in ins_goa(): {e}")
         self._logger.error(f"SQLpat: {sql}")
         self._logger.error(f"SQLparams: {params}")
         self._conn.rollback()
         return False
      if commit:
        try:
          self._conn.commit()
        except Error as e:
          self._logger.error(f"MySQL commit error in ins_goa(): {e}")
          self._conn.rollback()
          return False
    return True

  def ins_pathway(self, init, commit=True):
    if 'pwtype' in init and 'name' in init:
      pwtype = init['pwtype']
      name = init['name']
    else:
      self.warning(f"Invalid parameters sent to ins_pathway(): {init}")
      return False
    if 'protein_id' in init:
      cols = ['protein_id', 'pwtype', 'name']
      vals = ['%s','%s', '%s']
      params = [ init['protein_id'], pwtype, name ]
    elif 'target_id' in init:
      cols = ['target_id', 'pwtype', 'name']
      vals = ['%s','%s','%s']
      params = [ init['target_id'], pwtype, name ]
    else:
      self.warning(f"Invalid parameters sent to ins_pathway(): {init}")
      return False
    for optcol in ['id_in_source', 'description', 'url']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO pathway (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
         self._logger.error(f"MySQL Error in ins_pathway(): {e}")
         self._logger.error(f"SQLpat: {sql}")
         self._logger.error(f"SQLparams: {params}")
         self._conn.rollback()
         return False
      if commit:
        try:
          self._conn.commit()
        except Error as e:
          self._logger.error(f"MySQL commit error in ins_pathway(): {e}")
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

  def ins_phenotype(self, init, commit=True):
    if 'ptype' not in init:
      self.warning("Invalid parameters sent to ins_phenotype(): ", init)
      return False
    if 'protein_id' in init:
      cols = ['protein_id', 'ptype']
      vals = ['%s','%s']
      params = [init['protein_id'], init['ptype']]
    elif 'nhprotein_id' in init:
      cols = ['nhprotein_id', 'ptype']
      vals = ['%s','%s']
      params = [init['nhprotein_id'], init['ptype']]
    else:
      self.warning(f"Invalid parameters sent to ins_phenotype(): {init}")
      return False
    for optcol in ['trait', 'top_level_term_id', 'top_level_term_name', 'term_id', 'term_name', 'term_description', 'p_value', 'percentage_change', 'effect_size', 'procedure_name', 'parameter_name', 'gp_assoc', 'statistical_method', 'sex']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO phenotype (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, tuple(params))
      except Error as e:
        self._logger.error(f"MySQL Error in ins_phenotype(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_phenotype(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_expression(self, init, commit=True):
    if 'etype' in init and 'tissue' in init:
      params = [init['etype'], init['tissue']]
    else:
      self.warning(f"Invalid parameters sent to ins_expression(): {init}")
      return False
    cols = ['etype', 'tissue']
    vals = ['%s','%s']
    if 'protein_id' in init:
      cols = ['protein_id', 'etype', 'tissue']
      vals = ['%s','%s','%s']
      params.insert(0, init['protein_id'])
    elif 'target_id' in init:
      cols = ['target_id', 'etype', 'tissue']
      vals = ['%s','%s','%s']
      params.insert(0, init['target_id'])
    else:
      self.warning(f"Invalid parameters sent to ins_expression(): {init}")
      return False
    for optcol in ['qual_value', 'string_value', 'number_value', 'boolean_value', 'pubmed_id', 'evidence', 'zscore', 'conf', 'oid', 'confidence', 'url', 'cell_id', 'uberon_id']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO expression (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
        self._logger.error(f"MySQL Error in ins_expression(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_expression(): {e}")
        self._conn.rollback()
        return False
    return True

  def ins_feature(self, init, commit=True):
    if 'protein_id' in init and 'type' in init:
      params = [init['protein_id'], init['type']]
    else:
      self.warning(f"Invalid parameters sent to ins_feature(): {init}")
      return False
    cols = ['protein_id', 'type']
    vals = ['%s','%s']
    for optcol in ['description', 'srcid', 'evidence', 'position', 'begin', 'end']:
      if optcol in init:
        cols.append(optcol)
        vals.append('%s')
        params.append(init[optcol])
    sql = "INSERT INTO feature (%s) VALUES (%s)" % (','.join(cols), ','.join(vals))
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      try:
        curs.execute(sql, params)
      except Error as e:
        self._logger.error(f"MySQL Error in ins_feature(): {e}")
        self._logger.error(f"SQLpat: {sql}")
        self._logger.error(f"SQLparams: {params}")
        self._conn.rollback()
        return False
    if commit:
      try:
        self._conn.commit()
      except Error as e:
        self._logger.error(f"MySQL commit error in ins_feature(): {e}")
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
  
