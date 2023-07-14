#!/usr/bin/env python3
# Time-stamp: <2022-09-05 14:18:56 smathias>
""" Load Drug Central data into TCRD from TSV files.

Usage:
    load-DrugCentral.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-DrugCentral.py -h | --help

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
__copyright__ = "Copyright 2015-2022, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "6.0.1"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
import csv
from collections import defaultdict
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
DC_RELEASE = '20220705' ## Make sure this is correct!!!
TCLIN_FILE = f'../data/DrugCentral/tcrd{DC_RELEASE}/tclin.tsv'
TCHEM_FILE = f'../data/DrugCentral/tcrd{DC_RELEASE}/tchem_drugs.tsv'
DRUGINFO_FILE = f'../data/DrugCentral/tcrd{DC_RELEASE}/drug_info.tsv'
DRUGIND_FILE = f'../data/DrugCentral/tcrd{DC_RELEASE}/drug_indications.tsv'
DRUGNAME_FILE = f'../data/DrugCentral/tcrd{DC_RELEASE}/drug_names.tsv'
SRC_FILES = [os.path.basename(TCLIN_FILE),
             os.path.basename(TCHEM_FILE),
             os.path.basename(DRUGINFO_FILE),
             os.path.basename(DRUGIND_FILE),
             os.path.basename(DRUGNAME_FILE)]


def load(args, dba, logfile, logger):
  # First get mapping of DrugCentral names to ids
  name2id = {}
  line_ct = slmf.wcl(DRUGNAME_FILE)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} lines file {DRUGNAME_FILE}")
  with open(DRUGNAME_FILE, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    ct = 0
    skip_ct = 0
    for row in tsvreader:
      #STRUCT_ID       NAME
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      if row[0] == 'NA':
        skip_ct += 1
        continue
      dname = row[1].strip()
      dcid = int(row[0].strip())
      name2id[dname] = int(dcid)
  print("  Got {} drug_name to dcid mappings".format(len(name2id)))
  if skip_ct > 0:
    print(f"  Skipped {skip_ct} rows with DCID= 'NA'")
  
  # Next get drug info fields
  infos = {}
  line_ct = slmf.wcl(DRUGINFO_FILE)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} input lines in file {DRUGINFO_FILE}")
  with open(DRUGINFO_FILE, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    ct = 0
    for row in tsvreader:
      ct += 1
      infos[row[0]] = row[1]
  print(" Got {} entries in drug infos map".format(len(infos)))

  #
  # MOA activities
  #
  drug2tids = defaultdict(set)
  line_ct = slmf.wcl(TCLIN_FILE)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} lines from DrugDB MOA activities file {TCLIN_FILE}")

  with open(TCLIN_FILE, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    # uniprot swissprot       drug_name       act_value       act_type        action_type     source_name     reference       smiles  ChEMBL_Id
    ct = 0
    da_ct = 0
    err_ct = 0
    notfnd = []
    dba_err_ct = 0
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      up = row[0]
      sp = row[1]
      drug = row[2].strip()
      if drug not in name2id:
        err_ct += 1
        logger.warning(f"No DrugCentral id found for MoA drug: '{drug}'")
        continue
      dcid = name2id[drug]
      tids = dba.find_target_ids({'uniprot': up})
      if not tids:
        tids = dba.find_target_ids({'name': sp})
        if not tids:
          notfnd.append(f'{up}|{sp}')
          continue
      tid = tids[0]
      drug2tids[drug].add(tid)
      init = {'target_id': tid, 'drug': drug, 'dcid': dcid, 'has_moa': 1, 'source': row[5]}
      if row[3]:
        init['act_value'] = row[3]
      if row[4]:
        init['act_type'] = row[4]
      if row[5]:
        init['action_type'] = row[5]
      if row[6]:
        init['source'] = row[6]
      if row[7]:
        init['reference'] = row[7]
      if row[8]:
        init['smiles'] = row[8]
      if row[9]:
        init['cmpd_chemblid'] = row[9]
      if drug in infos:
        init['nlm_drug_info'] = infos[drug]
      rv = dba.ins_drug_activity(init)
      if rv:
        da_ct += 1
      else:
        dba_err_ct += 1
  print(f"{ct} DrugCentral Tclin rows processed.")
  print(f"  Inserted {da_ct} new drug_activity rows.")
  if notfnd:
    print("WARNNING: {} Uniprot/Swissprot Accessions NOT FOUND in TCRD:".format(len(notfnd)))
    for upsp in notfnd:
      print(f'{upsp}')
  if err_ct > 0:
    print(f"WARNNING: DrugCentral ID not found for {err_ct} drug names. See logfile {logfile} for details.")
  if dba_err_ct > 0:
    print(f"WARNNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  #
  # Non-MOA activities
  #
  line_ct = slmf.wcl(TCHEM_FILE)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} lines from Non-MOA activities file {TCHEM_FILE}")
  with open(TCHEM_FILE, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    # uniprot swissprot       drug_name       act_value       act_type        action_type     source_name     reference       smiles  ChEMBL_Id
    ct = 0
    da_ct = 0
    err_ct = 0
    notfnd = []
    dba_err_ct = 0
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      up = row[0]
      sp = row[1]
      drug = row[2].strip()
      if drug not in name2id:
        err_ct += 1
        logger.warning(f"No DrugCentral id found for drug: '{drug}'")
        continue
      dcid = name2id[drug]
      tids = dba.find_target_ids({'uniprot': up})
      if not tids:
        tids = dba.find_target_ids({'name': sp})
        if not tids:
          notfnd.append(f'{up}|{sp}')
          continue
      tid = tids[0]
      drug2tids[drug].add(tid)
      init = {'target_id': tid, 'drug': drug, 'dcid': dcid, 'has_moa': 0, 'source': row[5]}
      if row[3]:
        init['act_value'] = row[3]
      if row[4]:
        init['act_type'] = row[4]
      if row[5]:
        init['action_type'] = row[5]
      if row[6]:
        init['source'] = row[6]
      if row[7]:
        init['reference'] = row[7]
      if row[8]:
        init['smiles'] = row[8]
      if row[9]:
        init['chemblid'] = row[9]
      if drug in infos:
        init['nlm_drug_info'] = infos[drug]
      rv = dba.ins_drug_activity(init)
      if rv:
        da_ct += 1
      else:
        dba_err_ct += 1
  print(f"{ct} DrugCentral Tchem rows processed.")
  print(f"  Inserted {da_ct} new drug_activity rows.")
  if notfnd:
    print("WARNNING: {} Uniprot/Swissprot Accessions NOT FOUND in TCRD:".format(len(notfnd)))
    for upsp in notfnd:
      print(f'{upsp}')
  if err_ct > 0:
    print(f"WARNNING: DrugCentral ID not found for {err_ct} drug names. See logfile {logfile} for details.")
  if dba_err_ct > 0:
    print(f"WARNNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  #
  # Indications (diseases)
  #
  line_ct = slmf.wcl(DRUGIND_FILE)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} lines from indications file {DRUGIND_FILE}")
  with open(DRUGIND_FILE, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    # DRUG_ID DRUG_NAME       INDICATION_FDB  UMLS_CUI        SNOMEDCT_CUI    DOID
    ct = 0
    t2d_ct = 0
    notfnd = {}
    dba_err_ct = 0
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      slmf.update_progress(ct/line_ct)
      drug = row[1]
      if drug not in drug2tids:
        logger.warning(f"Drug name {drug} not in drug2tids dict.")
        notfnd[drug] = True
        continue
      init = {'protein_id': tid, 'dtype': 'DrugCentral Indication',
              'name': row[2], 'drug_name': drug}
      if row[5] != '':
        init['did'] = row[5]
      # try to find a MONDO ID
      mondoid = None
      if row[5] != '':
        mondoid = dba.find_mondoid({'db': 'DOID', 'value': row[5]})
      if not mondoid and row[3] != '':
        mondoid = dba.find_mondoid({'db': 'UMLS', 'value': row[3]})
      if mondoid:
        init['mondoid'] = mondoid
      for tid in drug2tids[drug]:
        # NB> Using target_id as protein_id works for now, but will not if/when we have multiple protein targets
        init['protein_id'] = tid
        rv = dba.ins_disease(init)
        if rv:
          t2d_ct += 1
        else:
          dba_err_ct += 1
  print(f"{ct} DrugCentral indication rows processed.")
  print(f"  Inserted {t2d_ct} new disease rows")
  if notfnd:
    print("WARNING: {} drugs names not in activity maps. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
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

  start_time = time.time()
  load(args, dba, logfile, logger)

  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'DrugCentral', 'source': "DrugCentral v{} TSV files: {}".format(DC_RELEASE, ', '.join(SRC_FILES)), 'app': PROGRAM, 'app_version': __version__, 'url': 'http://drugcentral.org/'} )
  if not dataset_id:
    assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
    sys.exit(1)
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'drug_activity'},
            {'dataset_id': dataset_id, 'table_name': 'disease', 'where_clause': "dtype = 'DrugCentral Indication'"} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, "Error inserting provenance. See logfile {logfile} for details."

  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
