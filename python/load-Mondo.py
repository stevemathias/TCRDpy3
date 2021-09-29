#!/usr/bin/env python3
# Time-stamp: <2021-09-28 12:17:10 smathias>
"""Load Mondo Ontology into TCRD.

Usage:
    load-Mondo.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-Mondo.py -h | --help

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
__version__   = "1.0.0"

import os,sys,time
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

def download(name):
  cfgd = [d for d in CONFIG if d['name'] == name][0]
  fn = cfgd['DOWNLOAD_DIR'] + cfgd['FILENAME']
  if os.path.exists(fn):
    os.remove(fn)
  url = cfgd['BASE_URL'] + cfgd['FILENAME']
  print(f"\nDownloading {url}")
  print(f"         to {fn}")
  urlretrieve(url, fn)
  print("Done.")

def parse_mondo(fn):
  print(f"Parsing Mondo file {fn}")
  parser = obo.Parser(fn)
  raw_mondo = {}
  for stanza in parser:
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
        # for now, just ignore parent source info, if any.
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
          #init['xrefs'].append({'db': db, 'value': val})
          init['xrefs'].append({'db': db, 'value': val, 'source': src})
    mondod[mondoid] = init
  print("  Got {} Mondo terms".format(len(mondod)))
  return mondod

def load_mondo(dba, logger, logfile, mondod, cfgd):
  mondo_ct = len(mondod)
  print(f"Loading {mondo_ct} MonDO terms")
  ct = 0
  ins_ct = 0
  dba_err_ct = 0
  for mondoid,md in mondod.items():
    ct += 1
    md['mondoid'] = mondoid
    if 'xrefs' in md:
      for xref in md['xrefs']:
        if 'source' in xref and 'source="MONDO:equivalentTo"' in xref['source']:
          xref['equiv_to'] = 1
        else:
          xref['equiv_to'] = 0
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
  dataset_id = dba.ins_dataset( {'name': 'Mondo', 'source': 'Mondo file {}, version {}'.format(cfgd['BASE_URL']+cfgd['FILENAME'], ver), 'app': PROGRAM, 'app_version': __version__, 'url': 'https://mondo.monarchinitiative.org/'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'mondo'} ,
            {'dataset_id': dataset_id, 'table_name': 'mondo_parent'},
            {'dataset_id': dataset_id, 'table_name': 'mondo_xref'} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  
  print(f"{ct} terms processed.")
  print(f"  Inserted {ins_ct} new mondo rows (w/ associated parents and xrefs)")
  if dba_err_ct:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

CONFIG = [{'name': 'Mondo', 'DOWNLOAD_DIR': '../data/purl.obolibrary.org/', 
            'BASE_URL': 'http://purl.obolibrary.org/obo/', 'FILENAME': 'mondo.obo',
            'parse_function': parse_mondo, 'load_function': load_mondo}]

if __name__ == '__main__':
  print("\n{} (v{}) [{}]:".format(PROGRAM, __version__, time.strftime("%c")))
  start_time = time.time()
  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print("\n[*DEBUG*] ARGS:\n{}\n".format(repr(args)))

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
    #download(name)
    parsed_ont = cfgd['parse_function'](cfgd['DOWNLOAD_DIR']+cfgd['FILENAME'])
    cfgd['load_function'](dba, logger, logfile, parsed_ont, cfgd)
    
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
