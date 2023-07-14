'''
Read/Search (ie. SELECT) methods for TCRD.DBadaptor 

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2022-09-02 15:03:52 smathias>
'''
from contextlib import closing
from collections import defaultdict
import logging

class ReadMethodsMixin:
  def get_target_ids(self):
    '''
    Function  : Get all TCRD target ids
    Arguments : N/A
    Returns   : A list of integers
    Scope     : Public
    '''
    sql = "SELECT id FROM target"
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql)
      ids = [row[0] for row in curs.fetchall()]
    return ids

  def get_protein_ids(self):
    '''
    Function  : Get all TCRD protein ids
    Arguments : N/A
    Returns   : A list of integers
    Scope     : Public
    '''
    sql = "SELECT id FROM protein"
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql)
      ids = [row[0] for row in curs.fetchall()]
    return ids


  def get_proteins(self):
    '''
    Function  : Get all TCRD protein rows.
    Arguments : N/A
    Returns   : A list of dictionaries
    Scope     : Public
    '''
    sql = "SELECT * FROM protein"
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute(sql)
      proteins = [row for row in curs.fetchall()]
    return proteins

  def get_targetprotein(self, id):
    '''
    Function  : Get data from target and protein tables by target.id.
    Arguments : N/A
    Returns   : Dictionary containing target and protein data
    Scope     : Public
    '''
    sql = "SELECT t.id, t.tdl, t.idg, t.fam, t.famext, p.name, p.description, p.uniprot, p.sym, p.geneid, p.stringid, p.family, p.dtoid, p.dtoclass FROM target t, t2tc, protein p WHERE t.id = %s AND t.id = t2tc.target_id AND t2tc.protein_id = p.id"
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute(sql, (id,))
      tp = curs.fetchone()
    return tp

  def get_domain_xrefs(self, pid):
    '''
    Function  : 
    Arguments : N/A
    Returns   : A list of dictionaries
    Scope     : Public
    '''
    xrefs = {}
    sql = "SELECT value, xtra FROM xref WHERE protein_id = %s AND xtype = %s"
    with closing(self._conn.cursor(dictionary=True)) as curs:
      for xt in ['Pfam', 'InterPro', 'PROSITE']:
        l = []
        curs.execute(sql, (pid, xt))
        xrefs[xt] = [d for d in curs.fetchall()]
    return xrefs

  def get_jlds(self, pid):
    '''
    Function  : 
    Arguments : N/A
    Returns   : A list of dictionaries
    Scope     : Public
    '''
    sql = "SELECT name, did, dtype, zscore, conf FROM disease WHERE protein_id = %s AND dtype like 'JensenLab%' ORDER BY zscore DESC"
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute(sql, (pid, ))
      jlds = [d for d in curs.fetchall()]
    return jlds

  def get_uniprots_tdls(self):
    '''
    Function  : Get all protein.uniprot and target.tdl values for export to UniProt Mapping file.
    Arguments : N/A
    Returns   : A list of dictionaries
    Scope     : Public
    '''
    sql = "SELECT p.uniprot, t.tdl FROM target t, protein p, t2tc WHERE t.id = t2tc.target_id AND t2tc.protein_id = p.id"
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute(sql)
      proteins = [row for row in curs.fetchall()]
    return proteins
  
  def find_target_ids(self, q, incl_alias=False):
    '''
    Function  : Find id(s) of target(s) that satisfy the input query criteria
    Arguments : A dictionary containing query criteria and an optional boolean flag
    Returns   : A list of integers, or False if no targets are found
    Examples  : Search by HGNC Gene Symbol:
                target_ids = dba.find_target_ids({'sym': 'CHERP'})
                Search by UniProt Accession, including aliases:
                target_ids = dba.find_target_ids({'uniprot': 'O00302'}, incl_alias=True)
                Search by name (ie. Swissprot Accession):
                target_ids = dba.find_target_ids({'name': '5HT1A_HUMAN'})
                Search by NCBI Gene ID:
                target_ids = dba.find_target_ids({'geneid': '167359'})
                Search by STRING ID:
                target_ids = dba.find_target_ids({'stringid': 'ENSP00000300161'})
    Scope     : Public
    Comments  : The incl_alias flag only works for symbol and uniprot queries, as these are the only identifier types in the alias table.
    '''
    sql ="SELECT target_id FROM t2tc, protein p WHERE t2tc.protein_id = p.id"
    if 'sym' in q:
      if incl_alias:
        sql += " AND p.sym = %s UNION SELECT protein_id FROM alias WHERE type = 'symbol' AND value = %s"
        params = (q['sym'], q['sym'])
      else:
        sql += " AND p.sym = %s"
        params = (q['sym'],)
    elif 'uniprot' in q:
      if incl_alias:
        sql += " AND p.uniprot = %s UNION SELECT protein_id FROM alias WHERE type = 'uniprot' AND value = %s"
        params = (q['uniprot'], q['uniprot'])
      else:
        sql += " AND p.uniprot = %s"
        params = (q['uniprot'],)
    elif 'name' in q:
      sql += " AND p.name = %s"
      params = (q['name'],)
    elif 'geneid' in q:
      sql += " AND p.geneid = %s"
      params = (q['geneid'],)
    elif 'stringid' in q:
      sql += " AND p.stringid = %s"
      params = (q['stringid'],)
    else:
      self.warning("Invalid query parameters sent to find_target_ids(): ", q)
      return False
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
  
    ids = []
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      ids = [row[0] for row in curs.fetchall()]
    return ids

  def find_target_ids_by_xref(self, q, ):
    '''
    Function  : Find id(s) of target(s) that satisfy the input query criteria of xref type and value
    Arguments : A distionary containing query criteria
    Returns   : A list of integers, or False if no targets are found
    Examples  : Find target(s) by RefSeq xref:
                tids = dba.find_target_ids_by_xref({'xtype': 'RefSeq', 'value': 'NM_123456'})
    Scope     : Public
    Comments  : 
    '''
    if 'xtype' not in q or 'value' not in q:
      self.warning(f"Invalid query parameters sent to find_target_ids_by_xref(): {q}")
      return False

    ids = set()
    # first look by target xrefs
    sql = "SELECT target_id FROM xref WHERE protein_id IS NULL AND xtype = %s AND value = %s"
    params = (q['xtype'], q['value'])
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      for row in curs.fetchall():
        ids.add(row[0])
    # then look by component xrefs
    sql ="SELECT t2tc.target_id FROM t2tc, protein p, xref x WHERE t2tc.protein_id = p.id and p.id = x.protein_id AND x.xtype = %s AND x.value = %s"
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      for row in curs.fetchall():
        ids.add(row[0])

    if len(ids) > 1:
      return list(ids)
    else:
      return False

  def find_protein_ids(self, q, incl_alias=False):
    '''
    Function  : Find id(s) of protein(s) that satisfy the input query criteria
    Arguments : A dictionary containing query criteria and an optional boolean flag
    Returns   : A list of integers, or False if no proteins are found
    Examples  : Search by HGNC Gene Symbol:
                target_ids = dba.find_protein_ids({'sym': 'CHERP'})
                Search by UniProt Accession, including aliases:
                target_ids = dba.find_protein_ids({'uniprot': 'O00302'}, incl_alias=True)
                Search by name (ie. Swissprot Accession):
                target_ids = dba.find_protein_ids({'name': '5HT1A_HUMAN'})
                Search by NCBI Gene ID:
                target_ids = dba.find_protein_ids({'geneid': '167359'})
                Search by STRING ID:
                target_ids = dba.find_protein_ids({'stringid': 'ENSP00000300161'})
    Scope     : Public
    Comments  : The incl_alias flag only works for symbol and uniprot queries, as these are the only identifier types in the alias table.
    '''
    sql ="SELECT id FROM protein WHERE "
    if 'sym' in q:
      if incl_alias:
        sql += "sym = %s UNION SELECT protein_id FROM alias WHERE type = 'symbol' AND value = %s"
        params = (q['sym'], q['sym'])
      else:
        sql += "sym = %s"
        params = (q['sym'],)
    elif 'uniprot' in q:
      if incl_alias:
        sql += "uniprot = %s UNION SELECT protein_id FROM alias WHERE type = 'uniprot' AND value = %s"
        params = (q['uniprot'], q['uniprot'])
      else:
        sql += "uniprot = %s"
        params = (q['uniprot'],)
    elif 'name' in q:
      sql += "name = %s"
      params = (q['name'],)
    elif 'geneid' in q:
      sql += "geneid = %s"
      params = (q['geneid'],)
    elif 'stringid' in q:
      sql += "stringid = %s"
      params = (q['stringid'],)
    else:
      self.warning("Invalid query parameters sent to find_protein_ids(): ", q)
      return False
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    ids = []
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      ids = [row[0] for row in curs.fetchall()]
    return ids

  def find_protein_ids_by_xref(self, q):
    '''
    Function  : Find id(s) of protein(s) that satisfy the input query criteria of xref type and value
    Arguments : A distionary containing query criteria
    Returns   : A list of integers, or False if no proteins are found
    Examples  : Find protein(s) by RefSeq xref:
                pids = dba.find_protein_ids_by_xref({'xtype': 'RefSeq', 'value': 'NM_123456'})
    Scope     : Public
    Comments  : 
    '''
    if 'xtype' not in q or 'value' not in q:
      self.warning(f"Invalid query parameters sent to find_target_ids_by_xref(): {q}")
      return False
    ids = set()
    sql = "SELECT protein_id FROM xref WHERE target_id IS NULL AND xtype = %s AND value = %s"
    params = (q['xtype'], q['value'])
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      ids = [row[0] for row in curs.fetchall()]
    return ids

  def find_nhprotein_ids(self, q, species=False):
    '''
    Function  : Find id(s) of nhprotein(s) that satisfy the input query criteria
    Arguments : A dictionary containing query criteria and an optional string specifying species
    Returns   : A list of integers, or False if no nhproteins are found
    Examples  : Search by HGNC Gene Symbol:
                nhprotein_ids = dba.find_nhprotein_ids({'sym': 'Dact2', 'species': 'Mus musculus'})
    Scope     : Public
    '''
    sql ="SELECT id FROM nhprotein WHERE "
    if 'sym' in q:
      if species:
        sql += "sym = %s AND species = %s"
        params = (q['sym'], species)
      else:
        sql += "sym = %s"
        params = (q['sym'],)
    elif 'uniprot' in q:
      if species:
        sql += "uniprot = %s AND species = %s"
        params = (q['uniprot'], species)
      else:
        sql += "uniprot = %s"
        params = (q['uniprot'],)
    elif 'geneid' in q:
      if species:
        sql += "geneid = %s AND species = %s"
        params = (q['geneid'], species)
      else:
        sql += "geneid = %s"
        params = (q['d'],)
    elif 'name' in q:
      if species:
        sql += "name = %s AND species = %s"
        params = (q['name'], species)
      else:
        sql += "name = %s"
        params = (q['name'],)
    else:
      self.warning("Invalid query parameters sent to find_nhprotein_ids(): ", q)
      return False
    self._logger.debug(f"SQLpat: {sql}")
    self._logger.debug(f"SQLparams: {params}")
    ids = []
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      ids = [row[0] for row in curs.fetchall()]
    return ids

  def get_target(self, id, annot=False, gacounts=False):
    '''
    Function  : Get target data by id
    Arguments : An integer and two optional booleans
    Returns   : Dictionary containing target data
    Example   : target = dba->get_target(42, annot=True) 
    Scope     : Public
    Comments : By default, this returns only data in the target and
                target component tables (ie. target, protein and/or
                nucleaic acid). To get all associated annotations
                (except Harmonizome gene attributes), call with
                annot=True. To include counts of Harmonizome gene
                attributes, call with gacounts=True.
    '''
    with closing(self._conn.cursor(dictionary=True)) as curs:
      self._logger.debug("ID: %s" % id)
      curs.execute("SELECT * FROM target WHERE id = %s", (id,))
      t = curs.fetchone()
      if not t: return False
      if annot:
        # tdl_info
        t['tdl_infos'] = {}
        curs.execute("SELECT * FROM tdl_info WHERE target_id = %s", (id,))
        for ti in curs:
          self._logger.debug("  tdl_info: %s" % str(ti))
          itype = ti['itype']
          val_col = self._info_types[itype]
          t['tdl_infos'][itype] = {'id': ti['id'], 'value': ti[val_col]}
        if not t['tdl_infos']: del(t['tdl_infos'])
        # tdl_updates
        t['tdl_updates'] = []
        curs.execute("SELECT * FROM tdl_update_log WHERE target_id = %s", (id,))
        for u in curs:
          u['datetime'] = str(u['datetime'])
          t['tdl_updates'].append(u)
          if not t['tdl_updates']: del(t['tdl_updates'])
        # xrefs
        t['xrefs'] = {}
        for xt in self._xref_types:
          l = []
          curs.execute("SELECT * FROM xref WHERE target_id = %s AND xtype = %s", (id, xt))
          for x in curs:
            init = {'id': x['id'], 'value': x['value']}
            if x['xtra']:
              init['xtra'] = x['xtra']
            l.append(init)
          if l:
            t['xrefs'][xt] = l
        if not t['xrefs']: del(t['xrefs'])
        # Drug Activity
        t['drug_activities'] = []
        curs.execute("SELECT * FROM drug_activity WHERE target_id = %s", (id,))
        for da in curs:
          t['drug_activities'].append(da)
        if not t['drug_activities']: del(t['drug_activities'])
        # Cmpd Activity
        t['cmpd_activities'] = []
        curs.execute("SELECT * FROM cmpd_activity WHERE target_id = %s", (id,))
        for ca in curs:
          t['cmpd_activities'].append(ca)
        if not t['cmpd_activities']: del(t['cmpd_activities'])
      # Components
      t['components'] = {}
      t['components']['protein'] = []
      curs.execute("SELECT * FROM t2tc WHERE target_id = %s", (id,))
      for tc in curs:
        if tc['protein_id']:
          p = self.get_protein(tc['protein_id'], annot, gacounts)
          t['components']['protein'].append(p)
        else:
          # for possible future targets with Eg. nucleic acid components
          pass
      return t
  
  def get_protein(self, id, annot=False, gacounts=False):
    '''
    Function  : Get protein data by id
    Arguments : An integer and two optional booleans
    Returns   : Dictionary containing target data
    Example   : target = dba->get_protein(42, annot=True) 
    Scope     : Public
    Comments : By default, this returns only data in the protein table.
               To get all associated annotations (except Harmonizome
               gene attributes), call with annot=True. To include counts
               of Harmonizome gene attributes, call with gacounts=True.
    '''
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute("SELECT * FROM protein WHERE id = %s", (id,))
      p = curs.fetchone()
      if not p: return False
      if annot:
        # aliases
        p['aliases'] = []
        curs.execute("SELECT * FROM alias WHERE protein_id = %s", (id,))
        for a in curs:
          p['aliases'].append(a)
        if not p['aliases']: del(p['aliases'])
        # tdl_info
        p['tdl_infos'] = {}
        curs.execute("SELECT * FROM tdl_info WHERE protein_id = %s", (id,))
        decs = []
        for ti in curs:
          itype = ti['itype']
          val_col = self._info_types[itype]
          if itype == 'Drugable Epigenome Class':
            decs.append( {'id': ti['id'], 'value': str(ti[val_col])} )
          else:
            p['tdl_infos'][itype] = {'id': ti['id'], 'value': str(ti[val_col])}
        if decs:
          p['tdl_infos']['Drugable Epigenome Class'] = decs
        # xrefs
        p['xrefs'] = {}
        for xt in self._xref_types:
          l = []
          curs.execute("SELECT * FROM xref WHERE protein_id = %s AND xtype = %s", (id, xt))
          for x in curs:
            init = {'id': x['id'], 'value': x['value']}
            if x['xtra']:
              init['xtra'] = x['xtra']
            l.append(init)
          if l:
            p['xrefs'][xt] = l
        # generifs
        p['generifs'] = []
        curs.execute("SELECT * FROM generif WHERE protein_id = %s", (id,))
        for gr in curs:
          p['generifs'].append({'id': gr['id'], 'pubmed_ids': gr['pubmed_ids'], 'text': gr['text']})
        if not p['generifs']: del(p['generifs'])
        # goas
        p['goas'] = []
        curs.execute("SELECT * FROM goa WHERE protein_id = %s", (id,))
        for g in curs:
          p['goas'].append(g)
        if not p['goas']: del(p['goas'])
        # pmscores
        p['pmscores'] = []
        curs.execute("SELECT * FROM pmscore WHERE protein_id = %s", (id,))
        for pms in curs:
          p['pmscores'].append(pms)
        if not p['pmscores']: del(p['pmscores'])
        # phenotypes
        p['phenotypes'] = []
        curs.execute("SELECT * FROM phenotype WHERE protein_id = %s", (id,))
        for pt in curs:
          p['phenotypes'].append(pt)
        if not p['phenotypes']: del(p['phenotypes'])
        # GWAS
        p['gwases'] = []
        curs.execute("SELECT * FROM gwas WHERE protein_id = %s", (id,))
        for gw in curs:
          p['gwases'].append(gw)
        if not p['gwases']: del(p['gwases'])
        # IMPC phenotypes (via Mouse ortholog)
        p['impcs'] = []
        curs.execute("SELECT DISTINCT pt.term_id, pt.term_name, pt.p_value FROM ortholog o, nhprotein nhp, phenotype pt WHERE o.symbol = nhp.sym AND o.species = 'Mouse' AND nhp.species = 'Mus musculus' AND nhp.id = pt.nhprotein_id AND o.protein_id = %s", (id,))
        for pt in curs:
          p['impcs'].append(pt)
        if not p['impcs']: del(p['impcs'])
        # RGD QTLs (via Rat ortholog)
        # TBD
        # diseases
        p['diseases'] = []
        bad_diseases = ['Disease', 'Disease by infectious agent', 'Bacterial infectious disease', 'Fungal infectious disease', 'Parasitic infectious disease', 'Viral infectious disease', 'Disease of anatomical entity', 'Cardiovascular system disease', 'Endocrine system disease', 'Gastrointestinal system disease', 'Immune system disease', 'Integumentary system disease', 'Musculoskeletal system disease', 'Nervous system disease', 'Reproductive system disease', 'Respiratory system disease', 'Thoracic disease', 'Urinary system disease', 'Disease of cellular proliferation', 'Benign neoplasm', 'Cancer', 'Pre-malignant neoplasm', 'Disease of mental health', 'Cognitive disorder', 'Developmental disorder of mental health', 'Dissociative disorder', 'Factitious disorder', 'Gender identity disorder', 'Impulse control disorder', 'Personality disorder', 'Sexual disorder', 'Sleep disorder', 'Somatoform disorder', 'Substance-related disorder', 'Disease of metabolism', 'Acquired metabolic disease', 'Inherited metabolic disorder', 'Genetic disease', 'Physical disorder', 'Syndrome']
        curs.execute("SELECT * FROM disease WHERE protein_id = %s ORDER BY zscore DESC", (id,))
        for d in curs:
          #if d['name'] not in bad_diseases:
          p['diseases'].append(d)
        if not p['diseases']: del(p['diseases'])
        # ortholog_diseases
        p['ortholog_diseases'] = []
        curs.execute("SELECT od.did, od.name, od.ortholog_id, od.score, o.taxid, o.species, o.db_id, o.geneid, o.symbol, o.name FROM ortholog o, ortholog_disease od WHERE o.id = od.ortholog_id AND od.protein_id = %s", (id,))
        for od in curs:
          p['ortholog_diseases'].append(od)
        if not p['ortholog_diseases']: del(p['ortholog_diseases'])
        # expression
        p['expressions'] = []
        curs.execute("SELECT * FROM expression WHERE protein_id = %s", (id,))
        for ex in curs:
          etype = ex['etype']
          val_col = self._expression_types[etype]
          ex['value'] = ex[val_col]
          del(ex['number_value'])
          del(ex['boolean_value'])
          del(ex['string_value'])
          p['expressions'].append(ex)
          #p['expressions'].append({'id': ex['id'], 'etype': etype, 'tissue': ex['tissue'], 'evidence': ex['evidence'], 'zscore': str(ex['zscore']), 'conf': ex['conf'], 'oid': ex['oid'], 'value': ex[val_col], 'qual_value': ex['qual_value'], 'confidence': ex['confidence'], 'gender': ex['gender']})
        if not p['expressions']: del(p['expressions'])
        # gtex
        p['gtexs'] = []
        curs.execute("SELECT * FROM gtex WHERE protein_id = %s", (id,))
        for gtex in curs:
          p['gtexs'].append(gtex)
        if not p['gtexs']: del(p['gtexs'])
        # compartments
        p['compartments'] = []
        curs.execute("SELECT * FROM compartment WHERE protein_id = %s", (id,))
        for comp in curs:
          p['compartments'].append(comp)
        if not p['compartments']: del(p['compartments'])
        # phenotypes
        p['phenotypes'] = []
        curs.execute("SELECT * FROM phenotype WHERE protein_id = %s", (id,))
        for pt in curs:
          p['phenotypes'].append(pt)
        if not p['phenotypes']: del(p['phenotypes'])
        # pathways
        p['pathways'] = []
        curs.execute("SELECT * FROM pathway WHERE protein_id = %s", (id,))
        for pw in curs:
          p['pathways'].append(pw)
        if not p['pathways']: del(p['pathways'])
        # pubmeds
        p['pubmeds'] = []
        curs.execute("SELECT pm.* FROM pubmed pm, protein2pubmed p2p WHERE pm.id = p2p.pubmed_id AND p2p.protein_id = %s", (id,))
        for pm in curs:
          p['pubmeds'].append(pm)
        if not p['pubmeds']: del(p['pubmeds'])
        # features
        p['features'] = {}
        curs.execute("SELECT * FROM feature WHERE protein_id = %s", (id,))
        for f in curs:
          ft = f['type']
          del(f['type'])
          if ft in p['features']:
            p['features'][ft].append(f)
          else:
            p['features'][ft] = [f]
        if not p['features']: del(p['features'])
        # panther_classes
        p['panther_classes'] = []
        curs.execute("SELECT pc.pcid, pc.name FROM panther_class pc, p2pc WHERE p2pc.panther_class_id = pc.id AND p2pc.protein_id = %s", (id,))
        for pc in curs:
          p['panther_classes'].append(pc)
        if not p['panther_classes']: del(p['panther_classes'])
        # orthologs
        p['orthologs'] = []
        curs.execute("SELECT * FROM ortholog WHERE protein_id = %s", (id,))
        for o in curs:
          p['orthologs'].append(o)
        if not p['orthologs']: del(p['orthologs'])
        ## DTO classification
        #if p['dtoid']:
        #  p['dto_classification'] = "::".join(self.get_protein_dto(p['dtoid']))
        # patent_counts
        p['patent_counts'] = []
        curs.execute("SELECT * FROM patent_count WHERE protein_id = %s", (id,))
        for pc in curs:
          p['patent_counts'].append(pc)
        if not p['patent_counts']: del(p['patent_counts'])
        # TIN-X Novelty and Importance(s)
        curs.execute("SELECT * FROM tinx_novelty WHERE protein_id = %s", (id,))
        row = curs.fetchone()
        if row:
          p['tinx_novelty'] = row['score']
        else:
          p['tinx_novelty'] = ''
        p['tinx_importances'] = []
        bad_diseases = ['disease', 'disease by infectious agent', 'bacterial infectious disease', 'fungal infectious disease', 'parasitic infectious disease', 'viral infectious disease', 'disease of anatomical entity', 'cardiovascular system disease', 'endocrine system disease', 'gastrointestinal system disease', 'immune system disease', 'integumentary system disease', 'musculoskeletal system disease', 'nervous system disease', 'reproductive system disease', 'respiratory system disease', 'thoracic disease', 'urinary system disease', 'disease of cellular proliferation', 'benign neoplasm', 'cancer', 'pre-malignant neoplasm', 'disease of mental health', 'cognitive disorder', 'developmental disorder of mental health', 'dissociative disorder', 'factitious disorder', 'gender identity disorder', 'impulse control disorder', 'personality disorder', 'sexual disorder', 'sleep disorder', 'somatoform disorder', 'substance-related disorder', 'disease of metabolism', 'acquired metabolic disease', 'inherited metabolic disorder', 'genetic disease', 'physical disorder', 'syndrome']
        curs.execute("SELECT td.name, ti.score FROM tinx_disease td, tinx_importance ti WHERE ti.protein_id = %s AND ti.disease_id = td.id ORDER BY ti.score DESC", (id,))
        for txi in curs:
          if txi['name'] not in bad_diseases:
            p['tinx_importances'].append({'disease': txi['name'], 'score': txi['score']})
        if not p['tinx_importances']: del(p['tinx_importances'])
        # gene_attribute counts
        if gacounts:
          p['gene_attribute_counts'] = {}
          curs.execute("SELECT gat.name AS type, COUNT(*) AS attr_count FROM gene_attribute_type gat, gene_attribute ga WHERE gat.id = ga.gat_id AND ga.protein_id = %s GROUP BY type", (id,))
          for gact in curs:
            p['gene_attribute_counts'][gact['type']] = gact['attr_count']
          if not p['gene_attribute_counts']: del(p['gene_attribute_counts'])
        # KEGG Nearest Tclin(s)
        p['kegg_nearest_tclins'] = []
        curs.execute("SELECT p.name, p.geneid, p.uniprot, p.description, n.* FROM protein p, kegg_nearest_tclin n WHERE p.id = tclin_id AND n.protein_id = %s", (id,))
        for knt in curs:
          p['kegg_nearest_tclins'].append(knt)
        if not p['kegg_nearest_tclins']: del(p['kegg_nearest_tclins'])
    return p

  def get_target4tdlcalc(self, id):
    '''
    Function  : Get a target and associated data required for TDL calculation
    Arguments : An integer
    Returns   : Dictionary containing target data.
    Scope     : Public
    '''
    with closing(self._conn.cursor(dictionary=True, buffered=True)) as curs:
      self._logger.debug("ID: %s" % id)
      curs.execute("SELECT * FROM target WHERE id = %s", (id,))
      t = curs.fetchone()
      if not t: return False
      # Drug Activities
      t['drug_activities'] = []
      curs.execute("SELECT * FROM drug_activity WHERE target_id = %s", (id,))
      for da in curs:
        t['drug_activities'].append(da)
      if not t['drug_activities']: del(t['drug_activities'])
      # Cmpd Activity
      t['cmpd_activities'] = []
      curs.execute("SELECT * FROM cmpd_activity WHERE target_id = %s", (id,))
      for ca in curs:
        t['cmpd_activities'].append(ca)
      if not t['cmpd_activities']: del(t['cmpd_activities'])
      #
      # Protein associated data needed for TDL calculation
      #
      t['components'] = {}
      t['components']['protein'] = []
      p = {}
      p['tdl_infos'] = {}
      p['generifs'] = []
      curs.execute("SELECT * FROM t2tc WHERE target_id = %s", (id,))
      t2tc = curs.fetchone() # for now, all targets just have a single protein
      p['id'] = t2tc['protein_id']
      curs.execute("SELECT * FROM tdl_info WHERE itype = 'JensenLab PubMed Score' AND protein_id = %s", (p['id'],))
      pms = curs.fetchone()
      p['tdl_infos']['JensenLab PubMed Score'] = {'id': pms['id'], 'value': str(pms['number_value'])}
      curs.execute("SELECT * FROM tdl_info WHERE itype = 'Experimental MF/BP Leaf Term GOA' AND protein_id = %s", (p['id'],))
      efl_goa = curs.fetchone()
      if efl_goa:
        p['tdl_infos']['Experimental MF/BP Leaf Term GOA'] = {'id': efl_goa['id'], 'value': '1'}
      curs.execute("SELECT * FROM tdl_info WHERE itype = 'Ab Count' AND protein_id = %s", (p['id'],))
      abct = curs.fetchone()
      p['tdl_infos']['Ab Count'] = {'id': abct['id'], 'value': str(abct['integer_value'])}
      curs.execute("SELECT * FROM generif WHERE protein_id = %s", (p['id'],))
      for gr in curs:
        p['generifs'].append({'id': gr['id'], 'pubmed_ids': gr['pubmed_ids'], 'text': gr['text']})
      if not p['generifs']: del(p['generifs'])
    t['components']['protein'].append(p)
    return t

  def get_target4impcrpt(self, id):
    '''
    Function  : Get a target with associated IMPC Ortholog Phenotypes
    Arguments : An integer
    Returns   : Dictionary containing target data.
    Scope     : Public
    '''
    with closing(self._conn.cursor(dictionary=True, buffered=True)) as curs:
      self._logger.debug("ID: %s" % id)
      curs.execute("SELECT * FROM target WHERE id = %s", (id,))
      t = curs.fetchone()
      if not t: return False
      # IMPC phenotypes (via Mouse ortholog) are protein-associated
      t['components'] = {}
      t['components']['protein'] = []
      curs.execute("SELECT * FROM protein WHERE id = %s", (id,))
      p = curs.fetchone()
      if not p: return False
      p['impcs'] = []
      curs.execute("SELECT DISTINCT o.symbol, pt.term_id, pt.term_name, pt.top_level_term_id, pt.top_level_term_name, pt.p_value, pt.percentage_change, pt.effect_size, pt.procedure_name, pt.parameter_name, pt.statistical_method FROM ortholog o, nhprotein nhp, phenotype pt WHERE o.symbol = nhp.sym AND o.species = 'Mouse' AND nhp.species = 'Mus musculus' AND nhp.id = pt.nhprotein_id AND pt.gp_assoc AND o.protein_id = %s", (id,))
      for pt in curs:
        p['impcs'].append(pt)
      if not p['impcs']:
        del(p['impcs'])
    t['components']['protein'].append(p)
    return t

  def get_tigas(self):
    '''
    Function  : Get distinct tiga.protein_id and tiga.ensg values (for extlinks).
    Arguments : N/A
    Returns   : A list of dictionaries
    Scope     : Public
    '''
    tigas = []
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute("SELECT DISTINCT protein_id, ensg FROM tiga")
      tigas = [row for row in curs.fetchall()]
    return tigas

  def get_tinx_pmids(self):
    pmids = []
    with closing(self._conn.cursor()) as curs:
      curs.execute("SELECT DISTINCT pmid FROM tinx_articlerank")
      pmids = [row[0] for row in curs.fetchall()]
    return pmids

  def get_pmids(self):
    pmids = []
    with closing(self._conn.cursor()) as curs:
      curs.execute("SELECT id FROM pubmed")
      pmids = [row[0] for row in curs.fetchall()]
    return pmids

  def get_missing_tinx_pmids(self):
    '''Returns strings, not ints, so ids can be sent to EUtils'''
    pmids = []
    with closing(self._conn.cursor()) as curs:
      sql = "SELECT DISTINCT pmid FROM tinx_articlerank WHERE pmid NOT IN (SELECT id FROM pubmed)"
      curs.execute(sql)
      pmids = [str(row[0]) for row in curs.fetchall()]
    return pmids

  def get_diseases(self, dtype=None, with_did=False):
    diseases = []
    sql = "SELECT * FROM disease"
    if dtype:
      if with_did:
        sql += f" WHERE dtype = '{dtype}' AND did IS NOT NULL"
      else:
        sql += f" WHERE dtype = '{dtype}'"
    elif with_did:
      sql += " WHERE did IS NOT NULL"
    with closing(self._conn.cursor(dictionary=True, buffered=True)) as curs:
      curs.execute(sql)
      diseases = [d for d in curs.fetchall()]
    return diseases
  
  def get_diseases_without_mondoid(self):
    diseases = []
    sql = "SELECT * FROM disease WHERE mondoid IS NULL"
    with closing(self._conn.cursor(dictionary=True, buffered=True)) as curs:
      curs.execute(sql)
      diseases = [d for d in curs.fetchall()]
    return diseases
  
  def find_uberon_id(self, q):
    if 'oid' in q:
      (db, val) = q['oid'].split(':')
      sql = "SELECT uid FROM uberon_xref WHERE db = %s AND value = %s"
      params = (db, val)
    elif 'name' in q:
      name = q['name'].lower()
      sql = "SELECT uid FROM uberon WHERE LOWER(name) = %s"
      params = (name,)
    else:
      self.warning("Invalid query parameters sent to find_uberon_id(): ", q)
      return False
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      row = curs.fetchone()
    if row:
      return row[0]
    else:
      return None

  def find_mondoid(self, q):
    if 'db' in q and 'value' in q:
      if q['db'] == 'MIM':
        db = 'OMIM'
      else:
        db = q['db']
      sql = "SELECT mondoid FROM mondo_xref WHERE db = %s AND value = %s AND equiv_to"
      params = (db, q['value'])
    elif 'name' in q:
      name = q['name'].lower()
      sql = "SELECT mondoid FROM mondo WHERE LOWER(name) = %s"
      params = (name,)
    else:
      self.warning("Invalid query parameters sent to find_mondo_id(): ", q)
      return False
    with closing(self._conn.cursor()) as curs:
      curs.execute(sql, params)
      row = curs.fetchone()
    if row:
      return row[0]
    else:
      return None

  def get_cmpd_activities(self, catype=None):
    cmpd_activities = []
    sql = "SELECT * FROM cmpd_activity"
    if catype:
      sql += " WHERE catype = '%s'" % catype
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute(sql)
      cmpd_activities = [row for row in curs.fetchall()]
    return cmpd_activities

  def get_drug_activities(self):
    drug_activities = []
    with closing(self._conn.cursor(dictionary=True)) as curs:
      curs.execute("SELECT * FROM drug_activity")
      drug_activities = [row for row in curs.fetchall()]
    return drug_activities
