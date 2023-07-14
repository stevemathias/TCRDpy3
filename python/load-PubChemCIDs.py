#!/usr/bin/env python3
# Time-stamp: <2022-09-06 11:20:20 smathias>
"""Load PubChem CIDs into TCRD from TSV file.

Usage:
    load-PubChemCIDs.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-PubChemCIDs.py -? | --help

Options:
  -h --dbhost DBHOST   : MySQL database host name [default: localhost]
  -n --dbname DBNAME   : MySQL database name [default: tcrevd]
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
__author__ = "Steve Mathias"
__email__ = "smathias@salud.unm.edu"
__org__ = "Translational Informatics Division, UNM School of Medicine"
__copyright__ = "Copyright 2017-2022, Steve Mathias"
__license__ = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__ = "3.1.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
from urllib.request import urlretrieve
import gzip
import csv
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
DOWNLOAD_DIR = '../data/ChEMBL/UniChem/'
UNICHEM_BASE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/wholeSourceMapping/src_id1/'
# For src info, see https://www.ebi.ac.uk/unichem/ucquery/listSources
CHEML2PC_FILE = 'src1src22.txt.gz'

def download(args):
  gzfn = DOWNLOAD_DIR + CHEML2PC_FILE
  if os.path.exists(gzfn):
    os.remove(gzfn)
  fn = gzfn.replace('.gz', '')
  if os.path.exists(fn):
    os.remove(fn)
  if not args['--quiet']:
    print("\nDownloading {}".format(UNICHEM_BASE_URL + CHEML2PC_FILE))
    print(f"         to {gzfn}")
  urlretrieve(UNICHEM_BASE_URL + CHEML2PC_FILE, gzfn)
  if not args['--quiet']:
    print(f"Uncompressing {gzfn}")
  ifh = gzip.open(gzfn, 'rb')
  ofh = open(fn, 'wb')
  ofh.write( ifh.read() )
  ifh.close()
  ofh.close()

def get_chembl2pc():
  fn = DOWNLOAD_DIR + CHEML2PC_FILE
  fn = fn.replace('.gz', '')
  line_ct = slmf.wcl(fn)
  print(f"\nProcessing {line_ct} lines in file {fn}")
  chembl2pc = {}
  with open(fn, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    ct = 0
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      chembl2pc[row[0]] = int(row[1])
  return chembl2pc

    
def load(args, dba, chembl2pc, logfile, logger):
  cmpd_activities = dba.get_cmpd_activities(catype = 'ChEMBL')
  ca_ct = len(cmpd_activities)
  if not args['--quiet']:
    print("\nLoading PubChem CIDs for {} ChEMBL cmpd_activities".format(len(cmpd_activities)))
  logger.info("Loading PubChem CIDs for {} ChEMBL cmpd_activities".format(len(cmpd_activities)))
  ct = 0
  pcid_ct = 0
  notfnd = set()
  dba_err_ct = 0
  for ca in cmpd_activities:
    ct += 1
    slmf.update_progress(ct/ca_ct)
    if ca['cmpd_id_in_src'] not in chembl2pc:
      notfnd.add(ca['cmpd_id_in_src'])
      continue
    pccid = chembl2pc[ca['cmpd_id_in_src']]
    rv = dba.do_update({'table': 'cmpd_activity', 'id': ca['id'],
                        'col': 'cmpd_pubchem_cid', 'val': pccid})
    if rv:
      pcid_ct += 1
    else:
      dba_err_ct += 1
  if notfnd:
    for chemblid in notfnd:
      logger.warning(f"No PubChem CID found for {chemblid}")
  print(f'{ct} ChEMBL cmpd_activities processed.')
  print(f'  Updated {pcid_ct} cmpd_activity rows with PubChem CIDs')
  if notfnd:
    print('  No PubChem CID found for {} ChEMBL IDs. See logfile {} for details.'.format(len(notfnd), logfile))
  if dba_err_ct:
    print(f'WARNNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.')
    
  drug_activities = dba.get_drug_activities()
  da_ct = len(drug_activities)
  if not args['--quiet']:
    print("\nLoading PubChem CIDs for {} drug activities".format(len(drug_activities)))
  logger.info("Loading PubChem CIDs for {} drug activities".format(len(drug_activities)))
  ct = 0
  pcid_ct = 0
  skip_ct = 0
  notfnd = set()
  dba_err_ct = 0
  for da in drug_activities:
    ct += 1
    slmf.update_progress(ct/da_ct)
    if not da['cmpd_chemblid']:
      skip_ct += 1
      continue
    if da['cmpd_chemblid'] not in chembl2pc:
      notfnd.add(da['cmpd_chemblid'])
      continue
    pccid = chembl2pc[da['cmpd_chemblid']]
    rv = dba.do_update({'table': 'drug_activity', 'id': da['id'],
                        'col': 'cmpd_pubchem_cid', 'val': pccid})
    if rv:
      pcid_ct += 1
    else:
      dba_err_ct += 1
  if notfnd:
    for chemblid in notfnd:
      logger.warning(f"No PubChem CID found for {chemblid}")
  print(f'{ct} drug activities processed.')
  print(f'  Updated {pcid_ct} drug_activity rows with PubChem CIDs')
  print(f'  Skipped {skip_ct} drug_activity rows with no ChEMBL ID')
  if notfnd:
    print('  No PubChem CID found for {} ChEMBL IDs. See logfile {} for details.'.format(len(notfnd), logfile))
  if dba_err_ct:
    print(f'WARNNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.')

          
if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  
  args = docopt(__doc__, version=__version__)
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

  download(args)
  chembl2pc = get_chembl2pc()
  if not args['--quiet']:
    print("Got {} ChEMBL to PubChem CID mappings.".format(len(chembl2pc)))
  load(args, dba, chembl2pc, logfile, logger)

  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'PubChem CIDs', 'source': 'File {}'.format(UNICHEM_BASE_URL+CHEML2PC_FILE), 'app': PROGRAM, 'app_version': __version__} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'cmpd_activity', 'column_name': 'pubchem_cid', 'comment': "Loaded from UniChem file mapping ChEMBL IDs to PubChem CIDs. See https://www.ebi.ac.uk/unichem/ucquery/listSources for info on UniChem id sources."},
            {'dataset_id': dataset_id, 'table_name': 'drug_activity', 'column_name': 'pubchem_cid', 'comment': "Loaded from UniChem file mapping ChEMBL IDs to PubChem CIDs. See https://www.ebi.ac.uk/unichem/ucquery/listSources for info on UniChem id sources."} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."

  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))

