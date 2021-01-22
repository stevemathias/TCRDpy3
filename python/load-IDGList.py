#!/usr/bin/env python3
# Time-stamp: <2021-01-21 11:31:00 smathias>
"""Load IDG Eligible flags into TCRD from CSV file.

Usage:
    load-IDGList.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-IDGList.py | --help

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
__copyright__ = "Copyright 2019-2020, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "3.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
import csv
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '7' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"
#IDG_LIST_FILE = '../data/IDG_Lists/IDG_List_20210120_forv6.csv'
IDG_LIST_FILE = '../data/IDG_Lists/IDG_List_20210120.csv'

def load(args, dba, logger, logfile):
  line_ct = slmf.wcl(IDG_LIST_FILE)
  print(f"\nProcessing {line_ct} lines in file {IDG_LIST_FILE}")
  logger.info(f"Processing {line_ct} lines in list file {IDG_LIST_FILE}")
  ct = 0
  idg_ct = 0
  fam_ct = 0
  notfnd = []
  multfnd = []
  dba_err_ct = 0
  with open(IDG_LIST_FILE, 'r') as ifh:
    csvreader = csv.reader(ifh)
    for row in csvreader:
      if ct == 0:
        header = row # header line
        ct += 1
        continue
      ct += 1
      slmf.update_progress(ct/line_ct)
      sym = row[0]
      fam = row[1]
      if fam == 'IonChannel':
        fam = 'IC'
      tids = dba.find_target_ids({'sym': sym})
      if not tids:
        notfnd.append(sym)
        continue
      if len(tids) > 1:
        multfnd.append(sym)
        continue
      rv = dba.do_update({'table': 'target', 'col': 'idg', 'id': tids[0], 'val': 1})
      if rv:
        idg_ct += 1
      else:
        db_err_ct += 1
      rv = dba.do_update({'table': 'target', 'col': 'fam', 'id': tids[0], 'val': fam})
      if rv:
        fam_ct += 1
      else:
        dba_err_ct += 1
  print(f"{ct} lines processed")
  print(f"{idg_ct} target rows updated with IDG flags")
  print(f"{fam_ct} target rows updated with fams")
  if notfnd:
    print("WARNING: No target found for {} symbols: {}".format(len(notfnd), ", ".join(notfnd)))
  if multfnd:
    print("WARNING: Multiple targets found for {} symbols: {}".format(len(multfnd), ", ".join(multfnd)))
  if dba_err_ct > 0:
    print(f"WARNING: {dba_err_ct} database errors occured. See logfile {logfile} for details.")
  

if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  start_time = time.time()

  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print(f"\n[*DEBUG*] ARGS:\nargs\n")
  if args['--logfile']:
    logfile =  args['--logfile']
  else:
    logfile = LOGFILE
  loglevel = int(args['--loglevel'])
  logger = logging.getLogger(__name__)
  logger.setLevel(loglevel)
  if not args['--debug']:
    logger.propagate = False # turns off console logging
  fh = logging.FileHandler(LOGFILE)
  fmtr = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  fh.setFormatter(fmtr)
  logger.addHandler(fh)

  dba_params = {'dbhost': args['--dbhost'], 'dbname': args['--dbname'], 'logger_name': __name__}
  dba = DBAdaptor(dba_params)
  dbi = dba.get_dbinfo()
  logger.info("Connected to TCRD database {} (schema ver {}; data ver {})".format(args['--dbname'], dbi['schema_ver'], dbi['data_ver']))
  if not args['--quiet']:
    print("Connected to TCRD database {} (schema ver {}; data ver {})".format(args['--dbname'], dbi['schema_ver'], dbi['data_ver']))

  load(args, dba, logger, logfile)
    
  # Dataset and Provenance
  dataset_id = dba.ins_dataset( {'name': 'IDG Eligible Targets List', 'source': f'IDG generated data in file {IDG_LIST_FILE}.', 'app': PROGRAM, 'app_version': __version__, 'comments': 'IDG Target Flags are archived on GitHub in repo https://github.com/druggablegenome/IDGTargets.', 'url': 'https://github.com/druggablegenome/IDGTargets'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'idg'},
            {'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'fam', 'where_clause': 'idg = 1'} ]
            #{'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'famext', 'where_clause': 'column_name == "fam"', 'where_clause': 'idg = 1'}
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."

  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))

