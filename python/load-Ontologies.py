#!/usr/bin/env python3
# Time-stamp: <2021-04-12 14:27:06 smathias>
"""Load Disease, Mammalian Phenotype, RGD Disease, MonDO and Uberon Ontologies into TCRD.

Usage:
    load-Ontologies.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-Ontologies.py -h | --help

Options:
  -h --dbhost DBHOST   : MySQL database host name [default: localhost]
  -n --dbname DBNAME   : MySQL database name [default: tcrdev]
  -l --logfile LOGF    : set log file name
  -v --loglevel LOGL   : set logging level [default: 30]
                         50: CRITICAL
                         40: ERROR
                         30: WARNING
                         20: INFO
                         10: DEBUG
                          0: NOTSET
  -q --quiet           : set output verbosity to minimal level
  -d --debug           : turn on debugging output
  -? --help            : print this message and exit 
"""
__author__    = "Steve Mathias"
__email__     = "smathias @salud.unm.edu"
__org__       = "Translational Informatics Division, UNM School of Medicine"
__copyright__ = "Copyright 2020-2021, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "2.0.0"

import os,sys,time,re
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
from urllib.request import urlretrieve
import logging
import obo
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"

def download(args, name):
  cfgd = [d for d in CONFIG if d['name'] == name][0]
  fn = cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME']
  if os.path.exists(fn):
    os.remove(fn)
  url = cfgd['BASE_URL'] + cfgd['FILENAME']
  if not args['--quiet']:
    print(f"\nDownloading {url}")
    print(f"         to {fn}")
  urllib.urlretrieve(url, fn)
  if not args['--quiet']:
    print("Done.")

def parse_do(args, fn):
  if not args['--quiet']:
    print(f"Parsing Disease Ontology file {fn}")
  do_parser = obo.Parser(fn)
  raw_do = {}
  for stanza in do_parser:
    if stanza.name != 'Term':
      continue
    raw_do[stanza.tags['id'][0].value] = stanza.tags
  dod = {}
  for doid,d in raw_do.items():
    if not doid.startswith('DOID:'):
      continue
    if 'is_obsolete' in d:
      continue
    init = {'doid': doid, 'name': d['name'][0].value}
    if 'def' in d:
      init['def'] = d['def'][0].value
    if 'is_a' in d:
      init['parents'] = []
      for parent in d['is_a']:
        init['parents'].append(parent.value)
    if 'xref' in d:
      init['xrefs'] = []
      for xref in d['xref']:
        if xref.value.startswith('http'):
          continue
        try:
          (db, val) = xref.value.split(':')
        except:
          pass
        init['xrefs'].append({'db': db, 'value': val})
    dod[doid] = init
  if not args['--quiet']:
    print("  Got {} Disease Ontology terms".format(len(dod)))
  return dod

def load_do(args, dba, logger, logfile, dod, cfgd):
  do_ct = len(dod)
  if not args['--quiet']:
    print(f"Loading {do_ct} Disease Ontology terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for doid,d in dod.items():
    ct += 1
    d['doid'] = doid
    rv = dba.ins_do(d)
    if rv:
      ins_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/do_ct)

  # Dataset
  # data-version field in the header of the OBO file has a relase version:
  # data-version: releases/2016-03-25
  for line in os.popen("head %s"%cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME']):
    if line.startswith("data-version:"):
      ver = line.replace('data-version: ', '')
      break
  dataset_id = dba.ins_dataset( {'name': 'Disease Ontology', 'source': 'File %s, version %s'%(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__, 'url': 'http://disease-ontology.org/'} )
  assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'do'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'do_xref'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  
  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new do rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def parse_mpo_owl(args, fn):
  if not args['--quiet']:
    print(f"Parsing Mammalian Phenotype Ontology file {fn}")
  mpo = []
  mpont = pronto.Ontology(fn)
  for term in mpont:
    if not term.id.startswith('MP:'):
      continue
    mpid = term.id
    name = term.name
    init = {'mpid': mpid, 'name': name}
    if term.parents:
      init['parent_id'] = term.parents[0].id
    if term.desc:
      if term.desc.startswith('OBSOLETE'):
        continue
      init['def'] = term.desc
    mpo.append(init)
  if not args['--quiet']:
    print("  Got {} Mammalian Phenotype Ontology terms".format(len(mpo)))
  return mpo

def parse_mpo(args, fn):
  if not args['--quiet']:
    print(f"Parsing Mammalian Phenotype Ontology file {fn}")
  mpo_parser = obo.Parser(open(fn))
  raw_mpo = {}
  for stanza in mpo_parser:
    if stanza.name != 'Term':
      continue
    raw_do[stanza.tags['id'][0].value] = stanza.tags
  mpod = {}
  for mpoid,d in raw_mpo.items():
    #if not mpoid.startswith('MPOID:'):
    #  continue
    if 'is_obsolete' in d:
      continue
    init = {'mpoid': mpoid, 'name': d['name'][0].value}
    if 'def' in d:
      init['def'] = d['def'][0].value
    if 'is_a' in d:
      init['parents'] = []
      for parent in d['is_a']:
        init['parents'].append(parent.value)
    if 'xref' in d:
      init['xrefs'] = []
      for xref in d['xref']:
        if xref.value.startswith('http'):
          continue
        try:
          (db, val) = xref.value.split(':')
        except:
          pass
        init['xrefs'].append({'db': db, 'value': val})
    mpod[mpoid] = init
  if not args['--quiet']:
    print("  Got {} Mammalian Phenotype Ontology terms".format(len(mpod)))
  return mpod

def load_mpo(args, dba, logger, logfile, mpod, cfgd):
  mpo_ct = len(mpod)
  if not args['--quiet']:
    print(f"Loading {mpo_ct} Mammalian Phenotype Ontology terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for mpoid,d in mpod.items():
    ct += 1
    d['mpoid'] = dmpoid
    rv = dba.ins_mpo(d)
    if rv:
      ins_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/mpo_ct)
      
  # Dataset
  # data-version field in the header of the OBO file has a relase version:
  # data-version: releases/2016-03-25
  for line in os.popen("head %s"%cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME']):
    if line.startswith("data-version:"):
      ver = line.replace('data-version: ', '')
      break
  dataset_id = dba.ins_dataset( {'name': 'Mammalian Phenotype Ontology', 'source': 'File %s, version %s'%(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__} )
  assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'mpo'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  
  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new mpo rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def parse_rdo(args, fn):
  if not args['--quiet']:
    print(f"Parsing RGD Disease Ontology file {fn}")
  rdo_parser = obo.Parser(open(fn))
  raw_rdo = {}
  for stanza in rdo_parser:
    if stanza.name != 'Term':
      continue
    raw_rdo[stanza.tags['id'][0].value] = stanza.tags
  rdod = {}
  for doid,d in raw_rdo.items():
    if not doid.startswith('DOID:'):
      continue
    if 'is_obsolete' in d:
      continue
    init = {'doid': doid, 'name': d['name'][0].value}
    if 'def' in d:
      init['def'] = d['def'][0].value
    # if 'is_a' in d:
    #   init['parents'] = []
    #   for parent in d['is_a']:
    #     init['parents'].append(parent.value)
    if 'alt_id' in d:
      init['xrefs'] = []
      for aid in d['alt_id']:
        if aid.value.startswith('http'):
          continue
        try:
          (db, val) = aid.value.split(':')
        except:
          pass
        init['xrefs'].append({'db': db, 'value': val})
    if 'xref' in d:
      if 'xrefs' not in init:
        init['xrefs'] = []
      for xref in d['xref']:
        if xref.value.startswith('http'):
          continue
        try:
          (db, val) = xref.value.split(':')
        except:
          pass
        init['xrefs'].append({'db': db, 'value': val})
    rdod[doid] = init
  if not args['--quiet']:
    print("  Got {} RGD Disease Ontology terms".format(len(rdod)))
  return rdod

def load_rdo(args, dba, logger, logfile, rdod, cfgd):
  rdo_ct = len(rdod)
  if not args['--quiet']:
    print(f"Loading {rdo_ct} RGD Disease Ontology terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for doid,d in rdod.items():
    ct += 1
    d['doid'] = doid
    rv = dba.ins_rdo(d)
    if rv:
      ins_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/rdo_ct)

  # Dataset
  # data-version field in the header of the OBO file has a relase version:
  # data-version: 1.28
  f = os.popen("head %s"%cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME'])
  for line in f:
    if line.startswith("data-version:"):
      ver = line.replace('data-version: ', '')
      break
  f.close()
  dataset_id = dba.ins_dataset( {'name': 'RGD Disease Ontology', 'source': 'File %s, version %s'%(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'rdo'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'rdo_xref'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."

  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new rdo rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def parse_uberon(args, fn):
  if not args['--quiet']:
    print(f"Parsing Uberon Ontology file {fn}")
  uber_parser = obo.Parser(fn)
  raw_uber = {}
  for stanza in uber_parser:
    if stanza.name != 'Term':
      continue
    raw_uber[stanza.tags['id'][0].value] = stanza.tags
  uberd = {}
  for uid,ud in raw_uber.items():
    if 'is_obsolete' in ud:
      continue
    if 'name' not in ud:
      continue
    init = {'uid': uid, 'name': ud['name'][0].value}
    if 'def' in ud:
      init['def'] = ud['def'][0].value
    if 'comment' in ud:
      init['comment'] = ud['comment'][0].value
    if 'is_a' in ud:
      init['parents'] = []
      for parent in ud['is_a']:
        # some parent values have a source ie. 'UBERON:0010134 {source="MA"}'
        # get rid of this for now
        cp = parent.value.split(' ')[0]
        init['parents'].append(cp)
    if 'xref' in ud:
      init['xrefs'] = []
      for xref in ud['xref']:
        if xref.value.startswith('http') or xref.value.startswith('url'):
          continue
        if len(xref.value.split(' ')) == 1:
          (db, val) = xref.value.split(':')
          if db.endswith('_RETIRED'):
            continue
          init['xrefs'].append({'db': db, 'value': val})
        else:
          (dbval, src) = xref.value.split(' ', 1)
          (db, val) = dbval.split(':')
          if db.endswith('_RETIRED'):
            continue
          init['xrefs'].append({'db': db, 'value': val, 'source': src})
    uberd[uid] = init
  if not args['--quiet']:
    print("  Got {} Uberon Ontology terms".format(len(uberd)))
  return uberd

def load_uberon(args, dba, logger, logfile, uberd, cfgd):
  uberon_ct = len(uberd)
  if not args['--quiet']:
    print(f"Loading {uberon_ct} Uberon terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for uid,ud in uberd.items():
    ct += 1
    ud['uid'] = uid
    rv = dba.ins_uberon(ud)
    if rv:
      ins_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/uberon_ct)

  # Dataset
  # data-version field in the header of the OBO file has a relase version:
  # data-version: releases/2016-03-25
  f = os.popen("head %s"%cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME'])
  for line in f:
    if line.startswith("data-version:"):
      ver = line.replace('data-version: ', '')
      break
  f.close()
  dataset_id = dba.ins_dataset( {'name': 'Uberon Ontology', 'source': 'File %s, version %s'%(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__, 'url': 'http://uberon.github.io/'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'uberon'} ,
            {'dataset_id': dataset_id, 'table_name': 'uberon_parent'},
            {'dataset_id': dataset_id, 'table_name': 'uberon_xref'} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  
  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new uberon rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def parse_mondo(args, fn):
  if not args['--quiet']:
    print(f"Parsing Mondo file {fn}")
  mondo_parser = obo.Parser(fn)
  raw_mondo = {}
  for stanza in mondo_parser:
    if stanza.name != 'Term':
      continue
    raw_mondo[stanza.tags['id'][0].value] = stanza.tags
  mondod = {}
  for mondoid,md in raw_mondo.items():
    if 'is_obsolete' in md:
      continue
    if 'name' not in md:
      continue
    init = {'mondoid': mondoid, 'name': md['name'][0].value}
    if 'def' in md:
      init['def'] = md['def'][0].value
    if 'comment' in md:
      init['comment'] = md['comment'][0].value
    if 'is_a' in md:
      init['parents'] = []
      for parent in md['is_a']:
        # for now, just ignore parent source infos, if any.
        cp = parent.value.split(' ')[0]
        init['parents'].append(cp)
    if 'xref' in md:
      init['xrefs'] = []
      for xref in md['xref']:
        if xref.value.startswith('http') or xref.value.startswith('url'):
          continue
        if len(xref.value.split(' ')) == 1:
          (db, val) = xref.value.split(':')
          init['xrefs'].append({'db': db, 'value': val})
        else:
          (dbval, src) = xref.value.split(' ', 1)
          (db, val) = dbval.split(':')
          init['xrefs'].append({'db': db, 'value': val, 'source': src})
    mondod[mondoid] = init
  if not args['--quiet']:
    print("  Got {} Mondo terms".format(len(mondod)))
  return mondod

def load_mondo(args, dba, logger, logfile, mondod, cfgd):
  mondo_ct = len(mondod)
  if not args['--quiet']:
    print(f"Loading {mondo_ct} Mondo terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for mondod,md in mondod.items():
    ct += 1
    ud['mondoid'] = mondoid
    rv = dba.ins_mondo(md)
    if rv:
      ins_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/mondo_ct)

  # Dataset
  # data-version field in the header of the OBO file has a relase version:
  # data-version: releases/2016-03-25
  f = os.popen("head %s"%cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME'])
  for line in f:
    if line.startswith("data-version:"):
      ver = line.replace('data-version: ', '')
      break
  f.close()
  dataset_id = dba.ins_dataset( {'name': 'Mondo', 'source': 'File %s, version %s'%(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__, 'url': 'https://github.com/monarch-initiative/mondo'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'mondo'} ,
            {'dataset_id': dataset_id, 'table_name': 'mondo_parent'},
            {'dataset_id': dataset_id, 'table_name': 'mondo_xref'} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  
  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new uberon rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")


CONFIG = [ {'name': 'Disease Ontology', 'DOWNLOAD_DIR': '../data/DiseaseOntology', 
              'BASE_URL': 'http://purl.obolibrary.org/obo/', 'FILENAME': 'doid.obo',
              'parse_function': parse_do, 'load_function': load_do},
           # {'name': 'Mammalian Phenotype Ontology', 'DOWNLOAD_DIR': '../data/MPO/', 
           #  'BASE_URL': 'http://www.informatics.jax.org/downloads/reports/', 'FILENAME': 'mp.owl',
           #    'parse_function': parse_mpo_owl, 'load_function': load_mpo},
           {'name': 'Mammalian Phenotype Ontology', 'DOWNLOAD_DIR': '../data/purl.obolibrary.org/', 
            'BASE_URL': 'http://purl.obolibrary.org/obo/', 'FILENAME': 'mp.obo',
              'parse_function': parse_mpo, 'load_function': load_mpo},
           {'name': 'RGD Disease Ontology', 'DOWNLOAD_DIR': '../data/RGD/', 
            'BASE_URL': 'ftp://ftp.rgd.mcw.edu/pub/ontology/disease/', 'FILENAME': 'RDO.obo',
              'parse_function':parse_rdo, 'load_function': load_rdo },
           # {'name': 'Mondo', 'DOWNLOAD_DIR': '../data/Mondo/', 
           #  'BASE_URL': 'http://purl.obolibrary.org/obo/mondo/',
           #  'FILENAME': 'mondo-with-equivalents.owl',
           #  'parse_function': parse_mondo_owl, 'load_function': load_mondo},
           {'name': 'Mondo', 'DOWNLOAD_DIR': '../data/purl.obolibrary.org/', 
            'BASE_URL': 'http://purl.obolibrary.org/obo/', 'FILENAME': 'mondo.obo',
            'parse_function': parse_mondo, 'load_function': load_mondo},
           {'name': 'Uberon Ontology', 'DOWNLOAD_DIR': '../data/purl.obolibrary.org/', 
            'BASE_URL': 'http://purl.obolibrary.org/obo/uberon/', 'FILENAME': 'ext.obo',
              'parse_function': parse_uberon, 'load_function': load_uberon} ]

if __name__ == '__main__':
  print "\n{} (v{}) [{}]:".format(PROGRAM, __version__, time.strftime("%c"))
  start_time = time.time()
  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print "\n[*DEBUG*] ARGS:\n%s\n"%repr(args)

  loglevel = int(args['--loglevel'])
  if args['--logfile']:
    logfile = args['--logfile']
  else:
    logfile = LOGFILE
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
  if not args['--debug']:
    logger.propagate = False # turns off console logging
    fh = logging.FileHandler(logfile)
    fmtr = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fmtr)
    logger.addHandler(fh)

  dba_params = {'dbhost': args['--dbhost'], 'dbname': args['--dbname'], 'logger_name': __name__}
  dba = DBAdaptor(dba_params)
  dbi = dba.get_dbinfo()
  logger.info("Connected to TCRD database {} (schema ver {}; data ver {})".format(args['--dbname'], dbi['schema_ver'], dbi['data_ver']))
  if not args['--quiet']:
    print("Connected to TCRD database {} (schema ver {}; data ver {})".format(args['--dbname'], dbi['schema_ver'], dbi['data_ver']))

  for cfgd in CONFIG:
    name = cfgd['name']
    download(args, name)
    parsed_ont = cfgd['parse_function'](args, cfgd['DOWNLOAD_DIR']+cfgd['FILENAME'])
    cfgd['load_function'](args, dba, logger, logfile, parsed_ont, cfgd)
    
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
