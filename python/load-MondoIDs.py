#!/usr/bin/env python3
# Time-stamp: <2021-10-07 15:33:22 smathias>
"""Load Mondo IDs into disease.mondoid based on existing disease.did or disease.name into TCRD.
   
Usage:
    load-MondoIDs.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-MondoIDs.py -h | --help

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
__version__   = "1.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
from collections import defaultdict
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"

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

  diseases = dba.get_diseases()
  dis_ct = len(diseases)
  print(f"Processing {dis_ct} disease rows")
  ct = 0
  notfnd = []
  name2mondoid = defaultdict(list)
  did2mondoid = defaultdict(list)
  upd_ct = 0
  dba_err_ct = 0
  for dis in diseases:
    ct += 1
    mondoid = None
    if dis['did']:
      (db, val) = dis['did'].split(':')
      mondoid = dba.find_mondoid({'db': db, 'value': val})
      if mondoid:
        did2mondoid[did].append(mondoid)
    if not mondoid:
      mondoid = dba.find_mondoid({'name': dis['name']})
      if mondoid:
        name2mondoid[dis['name']].append(mondoid)
    if not mondoid:
      notfnd.append(dis)
      continue
    rv = dba.do_update({'table': 'disease', 'id': dis['id'],
                        'col': 'mondoid', 'val': mondoid})
    if rv:
      upd_ct += 1
    else:
      dba_err_ct += 1
    slmf.update_progress(ct/dis_ct)
  print(f"{ct} disease rows processed.")
  print(f"  Updated {upd_ct} rows with mondoids")
  
  if dba_err_ct:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")
    
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))


# ct = 0
# notfnd = []
# name2mondoid = defaultdict(list)
# did2mondoid = defaultdict(list)
# upd_ct = 0
# for dis in diseases:
#     ct += 1
#     mondoid = None
#     if dis['did']:
#         (db, val) = dis['did'].split(':')
#         mondoid = dba.find_mondoid({'db': db, 'value': val})
#         if mondoid:
#             did2mondoid[dis['did']].append(mondoid)
#     if not mondoid:
#         mondoid = dba.find_mondoid({'name': dis['name']})
#         if mondoid:
#             name2mondoid[dis['name']].append(mondoid)
#     if not mondoid:
#         notfnd.append(dis)
#         continue
#     upd_ct += 1
