#!/usr/bin/env python3
# Time-stamp: <2022-09-06 12:34:00 smathias>
"""Load DRGC resource data into TCRD via RSS API.

Usage:
    load-DRGC_Resources.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-DRGC_Resources.py -? | --help

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
__copyright__ = "Copyright 2019-2022, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "5.0.0"

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
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"
# API Docs: https://rss.ccs.miami.edu/rss-apis/
RSS_API_BASE_URL = 'https://rss.ccs.miami.edu/rss-api/'

def get_target_data():
  url = f"{RSS_API_BASE_URL}target"
  resp = requests.get(url) # , verify=False
  if resp.status_code == 200:
    return resp.json()
  else:
    return False

def get_resource_data(idval):
  url = f"{RSS_API_BASE_URL}target/id?id={idval}"
  resp = requests.get(url) # , verify=False
  if resp.status_code == 200:
    return resp.json()
  else:
    return False

def load(args, dba, logger, logfile):
  if not args['--quiet']:
    print("\nGetting target resource data from RSS...")
  target_data = get_target_data()
  assert target_data, "Error getting target data: FATAL"
  rss_ct = len(target_data)
  ct = 0
  skip_ct = 0
  res_ct = 0
  tmark = set()
  notfnd = set()
  mulfnd = set()
  dba_err_ct = 0
  if not args['--quiet']:
    print(f"Processing {rss_ct} target resource records...")
  for td in target_data:
    logger.info("Processing target resource data: {}".format(td))
    ct += 1
    slmf.update_progress(ct/rss_ct)
    if not td['pharosReady']:
      skip_ct += 1
      continue
    sym = td['target']
    #rssid = td['id'].rsplit('/')[-1]
    rssid = td['id']
    resource_data = get_resource_data(rssid)
    dbjson = json.dumps(resource_data['data'][0]['resource'])
    tids = dba.find_target_ids({'sym': sym})
    if not tids:
      tids = dba.find_target_ids({'sym': sym}, incl_alias=True)
      if not tids:
        notfnd.add(sym)
        logger.warning("No target found for {}".format(sym))
        continue
    if len(tids) > 1:
      mulfnd.add(sym)
      logger.warning("Multiple targets found for {}".format(sym))
    tid = tids[0]
    rv = dba.ins_drgc_resource( {'rssid': rssid, 'resource_type': td['resourceType'],
                                 'target_id': tid, 'json': dbjson} )
    if not rv:
      dba_err_ct += 1
      continue
    tmark.add(tid)
    res_ct += 1
  print(f"{ct} RSS target resource records processed.")
  print(f"  Skipped {skip_ct} non-pharosReady resources.")
  print("Inserted {} new drgc_resource rows for {} targets".format(res_ct, len(tmark)))
  if notfnd:
    print("WARNING: No target found for {} symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if mulfnd:
    print("WARNING: Multiple targets found for {} symbols. See logfile {} for details.".format(len(mulfnd), logfile))
  if dba_err_ct > 0:
    print(f"ERROR: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")


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

  # delete existing DRGC resources and dataset, if any
  print("deleting existing DRGC Resources (if any)...")
  rv = dba.del_all_rows('drgc_resource')
  if type(rv) == int:
    print(f"  Deleted {rv} existing rows from drgc_resource.")
  else:
    print(f"Error deleting existing data from {tblname}. Exiting.")
    exit(1)
  rv = dba.del_dataset('DRGC Resources')
  if not rv:
    print(f"Error deleting dataset 'DRGC Resources'. Exiting.")
    exit(1)
  print("  Deleted existing DRGC Resources dataset/provenance.")

  start_time = time.time()
  load(args, dba, logger, logfile)
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'DRGC Resources', 'source': 'RSS APIs at ', 'app': PROGRAM, 'app_version': __version__} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'drgc_resource'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))

