#!/usr/bin/env python3
# Time-stamp: <2021-04-12 11:51:38 smathias>
"""Load links to external databases into TCRD.

Usage:
    load-Extlinks.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-Extlinks.py -? | --help

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
__copyright__ = "Copyright 2021, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "1.1.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import requests
import json
import logging
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
# GlyGen API Docs: https://api.glygen.org/
GLYGEN_PROTEIN_SEARCH_URL = 'https://api.glygen.org/directsearch/protein/?query=%7B%22uniprot_canonical_ac%22%3A%22{}%22%7D'
GLYGEN_PROTEIN_PAGE_URL = 'https://glygen.org/protein/{}'
TIGA_PAGE_URL = 'https://unmtid-shinyapps.net/shiny/tiga/?gene={}' #ENSG00000115977

def do_tiga(dba, logger, logfile):
  tigas = dba.get_tigas()
  tigact = len(tigas)
  print(f"\nLoading {tigact} TIGA ExtLinks for TCRD proteins")
  ct = 0
  el_ct = 0
  pmark = {}
  dba_err_ct = 0
  for d in tigas:
    ct += 1
    slmf.update_progress(ct/tigact)
    rv = dba.ins_extlink( {'source': 'TIGA', 'protein_id': d['protein_id'],
                           'url': TIGA_PAGE_URL.format(d['ensg'])} )
    if not rv:
      dba_err_ct += 1
      continue
    el_ct += 1
    pmark[d['protein_id']] = True
  print("Inserted {} new TIGA extlink rows for {} TCRD proteins.".format(el_ct, len(pmark)))
  if dba_err_ct > 0:
    print(f"ERROR: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

def do_glygen(dba, logger, logfile):
  proteins = dba.get_proteins()
  pct = len(proteins)
  print(f"\nChecking/Loading GlyGen ExtLinks for {pct} TCRD proteins")
  ct = 0
  el_ct = 0
  notfnd = set()
  api_err_ct = 0
  dba_err_ct = 0
  for p in proteins:
    logger.info(f"Processing protein {p['id']}: {p['uniprot']}")
    ct += 1
    slmf.update_progress(ct/pct)
    ingg = chk_glygen(p['uniprot'])
    if ingg == True:
      rv = dba.ins_extlink( {'source': 'GlyGen', 'protein_id': p['id'],
                             'url': GLYGEN_PROTEIN_PAGE_URL.format(p['uniprot'])} )
      if not rv:
        dba_err_ct += 1
        continue
      el_ct += 1
    elif ingg == False:
      logger.warn(f"No GlyGen record for {p['uniprot']}")
      notfnd.add(p['uniprot'])
      continue
    else:
      logger.Error("Unexpected GlyGen API result for {p['uniprot']}")
      api_err_ct += 1
      continue
  print(f"Processed {ct} TCRD proteins.")
  print(f"Inserted {el_ct} new GlyGen extlink rows.")
  if notfnd:
    print("No GlyGen record found for {} TCRD UniProts. See logfile {} for details.".format(len(notfnd), logfile))
  if api_err_ct > 0:
    print(f"WARNING: {api_err_ct} unexpected API responses. See logfile {logfile} for details.")
  if dba_err_ct > 0:
    print(f"ERROR: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

def chk_glygen(up):
  '''
  The GlyGen API returns 200 even if there is no corresponding protein page:
  In [4]: resp = requests.get( GLYGEN_PROTEIN_SEARCH_URL.format(up), verify=False )
  In [5]: resp
  Out[5]: <Response [200]>
  In [6]: resp.status_code
  Out[6]: 200
  In [13]: resp.json()['results']
  Out[13]: []
  In [14]: type(resp.json()['results'])
  Out[14]: list
  In [15]: len(resp.json()['results'])
  Out[15]: 0
  So we have to check the results list in the returned JSON
  '''
  resp = requests.get( GLYGEN_PROTEIN_SEARCH_URL.format(up), verify=False )
  if resp.status_code == 200:
    if len(resp.json()['results']) > 0:
      return True
    else:
      return False
  else:
    return None
    

if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  
  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print("\n[*DEBUG*] ARGS:\n{}\n".format(repr(args)))
  if args['--logfile']:
    logfile =  args['--logfile']
  else:
    logfile = LOGFILE
  loglevel = int(args['--loglevel'])
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

  start_time = time.time()
  do_glygen(dba, logger, logfile)
  do_tiga(dba, logger, logfile)
  
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'ExtLinks', 'source': 'Tested links to target/protein info in external resources.', 'app': PROGRAM, 'app_version': __version__} )
  assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'extlink'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
