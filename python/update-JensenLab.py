#!/usr/bin/env python3
# Time-stamp: <2022-01-12 14:35:44 smathias>
"""
Update JensenLab DISEASES and PubMedScore data in TCRD.

Usage:
    update-JensenLab.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    update-JensenLab.py -h | --help

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
__version__   = "1.1.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
from urllib.request import urlretrieve
import csv
import logging
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"

JL_BASE_URL = 'http://download.jensenlab.org/'
JL_DOWNLOAD_DIR = '../data/JensenLab/'
PM_SCORES_FILE = 'protein_counts.tsv' # in KMC dir on server
DISEASES_FILE_K = 'human_disease_knowledge_filtered.tsv'
DISEASES_FILE_E = 'human_disease_experiments_filtered.tsv'
DISEASES_FILE_T = 'human_disease_textmining_filtered.tsv'

def download_pmscores(args):
  if os.path.exists(JL_DOWNLOAD_DIR + PM_SCORES_FILE):
    os.remove(JL_DOWNLOAD_DIR + PM_SCORES_FILE)
  if not args['--quiet']:
    print(f"Downloading {JL_BASE_URL}KMC/{PM_SCORES_FILE}")
    print(f"         to {JL_DOWNLOAD_DIR}{PM_SCORES_FILE}")
  urlretrieve(f"{JL_BASE_URL}KMC/{PM_SCORES_FILE}", JL_DOWNLOAD_DIR + PM_SCORES_FILE)

def download_DISEASES(args):
  for fn in [DISEASES_FILE_K, DISEASES_FILE_E, DISEASES_FILE_T]:
    if os.path.exists(JL_DOWNLOAD_DIR + fn):
      os.remove(JL_DOWNLOAD_DIR + fn)
    if not args['--quiet']:
      print("Downloading {}".format(JL_BASE_URL + fn))
      print("         to {}".format(JL_DOWNLOAD_DIR + fn))
    urlretrieve(JL_BASE_URL + fn, JL_DOWNLOAD_DIR + fn)

def load_pmscores(dba, logger, logfile):
  ensp2pids = {} # ENSP => list of TCRD protein ids
  pmscores = {} # protein.id => sum(all scores)
  pms_ct = 0
  skip_ct = 0
  notfnd = set()
  dba_err_ct = 0
  infile = JL_DOWNLOAD_DIR + PM_SCORES_FILE
  line_ct = slmf.wcl(infile)
  print(f"Processing {line_ct} lines in file {infile}")
  with open(infile, 'rU') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    ct = 0
    for row in tsvreader:
      # sym  year  score
      ct += 1
      slmf.update_progress(ct/line_ct)
      if not row[0].startswith('ENSP'):
        skip_ct += 1
        continue
      ensp = row[0]
      if ensp in ensp2pids:
        # we've already found it
        pids = ensp2pids[ensp]
      elif ensp in notfnd:
        # we've already not found it
        continue
      else:
        pids = dba.find_protein_ids({'stringid': ensp})
        if not pids:
          pids = dba.find_protein_ids_by_xref({'xtype': 'STRING', 'value': '9606.'+ensp})
          if not pids:
            notfnd.add(ensp)
            logger.warn("No protein found for {}".format(ensp))
            continue
        ensp2pids[ensp] = pids # save this mapping so we only lookup each ENSP once
      for pid in pids:
        rv = dba.ins_pmscore({'protein_id': pid, 'year': row[1], 'score': row[2]} )
        if rv:
          pms_ct += 1
        else:
          dba_err_ct += 1
        if pid in pmscores:
          pmscores[pid] += float(row[2])
        else:
          pmscores[pid] = float(row[2])
  print(f"{ct} input lines processed.")
  print("  Inserted {} new pmscore rows for {} proteins".format(pms_ct, len(pmscores)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows w/o ENSP")
  if notfnd:
    print("  No protein found for {} STRING IDs. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  print("Updating {} JensenLab PubMed Scores...".format(len(pmscores)))
  ct = 0
  ti_ct = 0
  dba_err_ct = 0
  for pid,score in pmscores.items():
    ct += 1
    rv = dba.upd_pms_tdlinfo(pid, score)
    if rv:
      ti_ct += 1
    else:
      dba_err_ct += 1
  print(f"  Updated {ti_ct} 'JensenLab PubMed Score' tdl_info rows")
  if dba_err_ct:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def load_DISEASES(dba, logger, logfile):
  # Knowledge channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_K
  line_ct = slmf.wcl(fn)
  print(f"Processing {line_ct} lines in DISEASES Knowledge file {fn}")
  with open(fn, 'r') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    ct = 0
    k2pids = {} # ENSP|sym => list of TCRD protein ids
    pmark = {}
    skip_ct = 0
    notfnd = set()
    dis_ct = 0
    dba_err_ct = 0
    for row in tsvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      if not row[0].startswith('ENSP'):
        skip_ct += 1
        continue
      ensp = row[0]
      sym = row[1]
      k = "%s|%s"%(ensp,sym)
      if k in k2pids:
        # we've already found it
        pids = k2pids[k]
      elif k in notfnd:
        # we've already not found it
        continue
      else:
        pids = dba.find_protein_ids({'stringid': ensp})
        if not pids:
          pids = dba.find_protein_ids({'sym': sym})
          if not pids:
            notfnd.add(k)
            logger.warn(f"No protein found for {k}")
            continue
        k2pids[k] = pids # save this mapping so we only lookup each ENSP|sym once
      dtype = 'JensenLab Knowledge ' + row[4]
      for pid in pids:
        rv = dba.ins_disease( {'protein_id': pid, 'dtype': dtype, 'name': row[3],
                               'did': row[2], 'evidence': row[5], 'conf': row[6]} )
        if rv:
          dis_ct += 1
          pmark[pid] = True
        else:
          dba_err_ct += 1
  print(f"{ct} lines processed.")
  print("  Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows w/o ENSP")
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")
    
  # Experiment channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_E
  line_ct = slmf.wcl(fn)
  print(f"Processing {line_ct} lines in DISEASES Experiment file {fn}")
  with open(fn, 'rU') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    ct = 0
    k2pids = {} # ENSP|sym => list of TCRD protein ids
    pmark = {}
    notfnd = set()
    dis_ct = 0
    skip_ct = 0
    dba_err_ct = 0
    for row in tsvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      if not row[0].startswith('ENSP'):
        skip_ct += 1
        continue
      if row[2].startswith('ENSP'):
        skip_ct += 1
        continue
      ensp = row[0]
      sym = row[1]
      k = "%s|%s"%(ensp,sym)
      if k in k2pids:
        # we've already found it
        pids = k2pids[k]
      elif k in notfnd:
        # we've already not found it
        continue
      else:
        pids = dba.find_protein_ids({'stringid': ensp})
        if not pids:
          pids = dba.find_protein_ids({'sym': sym})
          if not pids:
            notfnd.add(k)
            logger.warn(f"No protein found for {k}")
            continue
        k2pids[k] = pids # save this mapping so we only lookup each ENSP|sym once
      dtype = 'JensenLab Experiment ' + row[4]
      for pid in pids:
        rv = dba.ins_disease( {'protein_id': pid, 'dtype': dtype, 'name': row[3],
                               'did': row[2], 'evidence': row[5], 'conf': row[6]} )
        if rv:
          dis_ct += 1
          pmark[pid] = True
        else:
          dba_err_ct += 1
  print(f"{ct} lines processed.")
  print("  Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows w/o ENSP or with ENSP did")
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

  # Text Mining channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_T
  line_ct = slmf.wcl(fn)
  print(f"Processing {line_ct} lines in DISEASES Textmining file {fn}")
  with open(fn, 'rU') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    ct = 0
    k2pids = {} # ENSP|sym => list of TCRD protein ids
    pmark = {}
    notfnd = set()
    dis_ct = 0
    skip_ct = 0
    dba_err_ct = 0
    for row in tsvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      if not row[0].startswith('ENSP'):
        skip_ct += 1
        continue
      if float(row[5]) < 3.0:
        # skip rows with confidence < 3.0
        skip_ct += 1
        continue
      ensp = row[0]
      sym = row[1]
      k = "%s|%s"%(ensp,sym)
      if k in k2pids:
        # we've already found it
        pids = k2pids[k]
      elif k in notfnd:
        # we've already not found it
        continue
      else:
        pids = dba.find_protein_ids({'stringid': ensp})
        if not pids:
          pids = dba.find_protein_ids({'sym': sym})
          if not pids:
            notfnd.add(k)
            logger.warn(f"No protein found for {k}")
            continue
        k2pids[k] = pids # save this mapping so we only lookup each ENSP|sym once
      dtype = 'JensenLab Text Mining'
      for pid in pids:
        rv = dba.ins_disease( {'protein_id': pid, 'dtype': dtype, 'name': row[3],
                               'did': row[2], 'zscore': row[4], 'conf': row[5]} )
        if rv:
          dis_ct += 1
          pmark[pid] = True
        else:
          dba_err_ct += 1
  print(f"{ct} lines processed.")
  print("  Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows w/o ENSP or with confidence < 3")
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")


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

  # for the time being, this has to be done manually because Lars is forcing https
  # -SLM 20210227
  #print("\nDownloading new JensenLab files...")
  #download_pmscores(args)
  #download_DISEASES(args)

  start_time = time.time()
  print("\nUpdating JensenLab PubMed Text-mining Scores...")
  # delete existing pmscores
  rv = dba.del_all_rows('pmscore')
  if type(rv) == int:
    print(f"  Deleted {rv} rows from pmscore")
  else:
    print(f"Error deleting rows from pmscore. Exiting.")
    exit(1)
  # set all existing 'JensenLab PubMed Score' TDL Infos to zero
  # This is so we don't have to redo inserting zero values for proteins with no score
  rv = dba.upd_pmstdlis_zero()
  if type(rv) == int:
    print(f"  Reset {rv} 'JensenLab PubMed Score' tdl_info values to zero.")
  else:
    print(f"Error updating 'JensenLab PubMed Score' tdl_info values. Exiting.")
    exit(1)
  # load new pmsores and update 'JensenLab PubMed Score' TDL Infos
  load_pmscores(dba, logger, logfile)
  # update dataset
  upds = {'app': PROGRAM, 'app_version': __version__,
          'source': f"File {JL_BASE_URL}KMC/{PM_SCORES_FILE}",
          'datetime': time.strftime("%Y-%m-%d %H:%M:%S")}
  rv = dba.upd_dataset_by_name('JensenLab PubMed Text-mining Scores', upds)
  assert rv, "Error updating dataset 'JensenLab PubMed Text-mining Scores'. Exiting."

  print("\nUpdating JensenLab DISEASES...")
  # delete existing DISEASES
  rv = dba.del_diseases('DISEASES')
  if type(rv) == int:
    print(f"  Deleted {rv} JensenLab rows from disease")
  else:
    print(f"Error deleting JensenLab rows from disease. Exiting.")
    exit(1)
  # load new DISEAESES
  load_DISEASES(dba, logger, logfile)
  # update dataset
  upds = {'app': PROGRAM, 'app_version': __version__,
          'datetime': time.strftime("%Y-%m-%d %H:%M:%S")}
  rv = dba.upd_dataset_by_name('JensenLab DISEASES', upds)
  assert rv, "Error updating dataset 'JensenLab DISEASES'. Exiting."

  # TISSUES
  # COMPARTMENTS
  
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
