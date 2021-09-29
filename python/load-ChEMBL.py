#!/usr/bin/env python3
# Time-stamp: <2021-05-06 13:33:16 smathias>
"""Load cmpd_activity data into TCRD from ChEMBL MySQL database.

Usage:
    load-ChEMBL.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-ChEMBL.py -h | --help

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
__copyright__ = "Copyright 2015-2021, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "6.1.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import mysql.connector
from mysql.connector import Error
from contextlib import closing
from urllib.request import urlretrieve
import csv
from operator import itemgetter
import copy
import logging
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
CHEMBL_DB = 'chembl_28'
DOWNLOAD_DIR = '../data/ChEMBL/'
BASE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/'
UNIPROT2CHEMBL_FILE = 'chembl_uniprot_mapping.txt'
# compounds/activities from publications (ie. src_id = 1, src_description = 'Scientific Literature')
#SQLq1 = "SELECT acts.molregno, md.pref_name, md.chembl_id, cs.canonical_smiles, acts.pchembl_value, acts.standard_type, cr.compound_name, d.journal, d.year, d.volume, d.issue, d.first_page, d.pubmed_id FROM activities acts, compound_records cr, assays a, target_dictionary t, compound_structures cs, molecule_dictionary md, docs d WHERE acts.record_id = cr.record_id AND cs.molregno = md.molregno AND cs.molregno = acts.molregno AND acts.assay_id = a.assay_id AND a.tid = t.tid AND t.chembl_id = %s AND acts.molregno = md.molregno AND a.assay_type = 'B' AND md.structure_type = 'MOL' AND acts.standard_flag = 1 AND acts.standard_relation = '=' AND t.target_type = 'SINGLE PROTEIN' AND acts.pchembl_value IS NOT NULL AND acts.doc_id = d.doc_id"
# patent compounds/activities from patents (ie. src_id = 38, src_description = 'Patent Bioactivity Data')
#SQLq2 = "SELECT acts.molregno, md.pref_name, md.chembl_id, cs.canonical_smiles, acts.pchembl_value, acts.standard_type, cr.compound_name FROM activities acts, compound_records cr, assays a, target_dictionary t, compound_structures cs, molecule_dictionary md WHERE acts.record_id = cr.record_id AND cs.molregno = md.molregno AND cs.molregno = acts.molregno AND acts.assay_id = a.assay_id AND a.tid = t.tid AND t.chembl_id = %s AND acts.molregno = md.molregno AND a.assay_type = 'B' AND md.structure_type = 'MOL' AND acts.standard_flag = 1 AND acts.standard_relation = '=' AND t.target_type = 'SINGLE PROTEIN' AND acts.pchembl_value IS NOT NULL AND cr.src_id = 38"

SQLq1 = '''
SELECT acts.molregno, md.pref_name, md.chembl_id, cs.canonical_smiles, acts.pchembl_value,
       acts.standard_type, cr.compound_name, d.journal, d.year, d.volume, d.issue, d.first_page,
       d.pubmed_id
FROM activities acts, compound_records cr, assays a, target_dictionary t, compound_structures cs,
     molecule_dictionary md, docs d
WHERE acts.record_id = cr.record_id
  AND cs.molregno = md.molregno
  AND cs.molregno = acts.molregno
  AND acts.assay_id = a.assay_id
  AND acts.molregno = md.molregno
  AND acts.doc_id = d.doc_id
  AND a.tid = t.tid
  AND t.target_type = 'SINGLE PROTEIN'
  AND acts.standard_type IN  ('IC50', 'Ki', 'Kb', 'Kd', 'EC50', 'AC50', 'XC50', 'pA2', 'Km')
  AND md.structure_type = 'MOL'
  AND acts.standard_flag = 1
  AND acts.standard_relation = '='
  AND acts.pchembl_value IS NOT NULL
  AND t.chembl_id = %s
'''
SQLq2 = '''
SELECT acts.molregno, md.pref_name, md.chembl_id, cs.canonical_smiles, acts.pchembl_value, 
       acts.standard_type, cr.compound_name
FROM activities acts, compound_records cr, assays a, target_dictionary t, compound_structures cs, 
     molecule_dictionary md
WHERE acts.record_id = cr.record_id
  AND cs.molregno = md.molregno
  AND cs.molregno = acts.molregno
  AND acts.assay_id = a.assay_id
  AND acts.molregno = md.molregno
  AND a.tid = t.tid
  AND t.target_type = 'SINGLE PROTEIN'
  AND acts.standard_type IN  ('IC50', 'Ki', 'Kb', 'Kd', 'EC50', 'AC50', 'XC50', 'pA2', 'Km')
  AND md.structure_type = 'MOL'
  AND acts.standard_flag = 1
  AND acts.standard_relation = '='
  AND acts.pchembl_value IS NOT NULL
  AND cr.src_id = 38
  AND t.chembl_id = %s
'''

CUTOFFS = {
  'GPCR': 7.0,  # 100nM
  'IC': 5.0, # 10uM
  'Kinase': 7.52288, # 30nM
  'NR': 7.0 # 100nM
}

def download_mappings():
  if os.path.exists(DOWNLOAD_DIR + UNIPROT2CHEMBL_FILE):
    os.remove(DOWNLOAD_DIR + UNIPROT2CHEMBL_FILE)
  print(f"\nDownloading {BASE_URL}{UNIPROT2CHEMBL_FILE}")
  print(f"         to {DOWNLOAD_DIR}{UNIPROT2CHEMBL_FILE}")
  urlretrieve(f"{BASE_URL}{UNIPROT2CHEMBL_FILE}", DOWNLOAD_DIR + UNIPROT2CHEMBL_FILE)

def load(args, dba, up2chembl, chembldb, logfile, logger):
  upct = len(up2chembl)
  if not args['--quiet']:
    print(f"\nProcessing {upct} UniProt accessions in up2chembl")
  ct = 0
  dba_err_ct = 0
  notfnd = set()
  nic_ct = 0
  nga_ct = 0
  tdl_ct = 0
  ca_ct = 0
  cyti_ct = 0
  csti_ct = 0
  t2acts = {}
  c2acts = {}
  for up in up2chembl.keys():
    ct += 1
    slmf.update_progress(ct/upct)
    tids = dba.find_target_ids({'uniprot': up}, incl_alias=True)
    if not tids:
      notfnd.add(up)
      logger.warn(f"No TCRD target found for UniProt {up}")
      continue
    tid = tids[0]
    tp = dba.get_targetprotein(tid)
    logger.info(f"Processing ChEMBL data for UniProt {up}: target {tid}")
    chembl_acts = []
    for ctid in up2chembl[up]:
      # Query 1
      with closing(chembldb.cursor(dictionary=True)) as curs:
        curs.execute(SQLq1, (ctid,))
        for d in curs:
          if d['year']:
            d['reference'] = "{}, ({}) {}:{}:{}".format(d['journal'], d['year'], d['volume'], d['issue'], d['first_page'])
          else:
            d['reference'] = "{}, {}:{}:{}".format(d['journal'], d['volume'], d['issue'], d['first_page'])
          for k in ['journal', 'volume', 'issue', 'first_page']:
            del(d[k])
          chembl_acts.append(d)
      # Query 2
      with closing(chembldb.cursor(dictionary=True)) as curs:
        curs.execute(SQLq2, (ctid,))
        for d in curs:
          d['reference'] = None
          chembl_acts.append(d)
    if tp['fam'] in CUTOFFS:
      cutoff =  CUTOFFS[tp['fam']]
    else:
      cutoff = 6.0 # 1uM for other families
    logger.info(f"Filter cutoff for {up} (target id {tid}) is {cutoff}")
    filtered_acts = [a for a in chembl_acts if a['pchembl_value'] >= cutoff]
    logger.info("{} ChEMBL acts => {} filtered acts".format(len(chembl_acts), len(filtered_acts)))
    if not filtered_acts:
     nga_ct += 1
     continue
    
    #
    # if we get here, the target has qualifying activites (and is thus Tchem)
    #
    # sort filtered activities by pchembl_value (descending), so that the
    # activity with the largest will be sorted_by_pchembl_value[0]
    sorted_by_pchembl_value = sorted(filtered_acts, key=itemgetter('pchembl_value'), reverse=True)
    
    # load TCRD cmpd_activities
    # The most potent activity value for a given target will be this one:
    # MIN(cmpd_activity.id) WHERE catype = 'ChEMBL' AND target_id = 3000
    for a in sorted_by_pchembl_value:
      if 'pubmed_id' in a:
        pmid = a['pubmed_id']
      else:
        pmid = None
      try:
        rv = dba.ins_cmpd_activity( {'target_id': tid, 'catype': 'ChEMBL', 'cmpd_id_in_src': a['chembl_id'], 'cmpd_name_in_src': a['compound_name'], 'smiles': a['canonical_smiles'], 'reference': a['reference'], 'act_value': a['pchembl_value'], 'act_type': a['standard_type'], 'pubmed_ids': pmid} )
      except:
        # some names have weird hex characters and cause errors, so replace w/ ?
        rv = dba.ins_cmpd_activity( {'target_id': tid, 'catype': 'ChEMBL', 'cmpd_id_in_src': a['chembl_id'], 'cmpd_name_in_src': '?', 'smiles': a['canonical_smiles'], 'reference': a['reference'], 'act_value': a['pchembl_value'], 'act_type': a['standard_type'], 'pubmed_ids': pmid} )
      if rv:
        ca_ct += 1
      else:
        dba_err_ct += 1
    
    # Save First ChEMBL Reference Year tdl_info, if there is one
    yrs = [a['year'] for a in filtered_acts if 'year' in a and a['year']]
    if len(yrs) > 0:
      first_year = min(yrs)
      rv = dba.ins_tdl_info( {'target_id': tid, 'itype': 'ChEMBL First Reference Year', 'integer_value': first_year} )
      if rv:
        cyti_ct += 1
      else:
        dba_err_ct += 1

    # Save mappings for selective compound calculations
    t2acts[tid] = copy.copy(sorted_by_pchembl_value)
    for a in chembl_acts:
      ac = copy.copy(a)
      smi = ac['canonical_smiles']
      del(ac['canonical_smiles'])
      ac['tid'] = tid
      ac['tname'] = tp['name']
      if smi in c2acts:
        c2acts[smi].append(ac)
      else:
        c2acts[smi] = [ac]
  print(f"{ct} UniProt accessions processed.")
  if notfnd:
    print("  No TCRD target found for {} UniProt accessions. See logfile {} for details.".format(len(notfnd), logfile))
  if nic_ct > 0:
    print(f"  {nic_ct} targets not found in ChEMBL")
  print(f"  {nga_ct} targets have no qualifying activities in ChEMBL")
  print(f"Inserted {ca_ct} new cmpd_activity rows")
  print(f"Inserted {cyti_ct} new 'ChEMBL First Reference Year' tdl_info rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  # Selective compound calculations
  if not args['--quiet']:
    print("\nRunning selective compound analysis...")
  c2macts = {}
  for c,acts in c2acts.items():
    if len(acts) > 1:
      c2macts[c] = list(acts)
  # then sort the activity lists by pchembl_value
  c2smacts = {}
  for c,acts in c2macts.items():
    c2smacts[c] = sorted(acts, key=itemgetter('pchembl_value'))
  selective = []
  for smi in c2smacts.keys():
    i = 1
    while i <= len(c2smacts[smi])-1:
      if c2smacts[smi][i]['tid'] == c2smacts[smi][i-1]['tid']:
        i += 1
        continue
      diff = c2smacts[smi][i]['pchembl_value'] - c2smacts[smi][i-1]['pchembl_value']
      if diff >= 2:
        selective.append(smi)
        break
      i += 1
  if not args['--quiet']:
    print("  Found {} selective compounds".format(len(selective)))
  cscti_ct = 0
  dba_err_ct = 0
  for tid,acts in t2acts.items():
    for a in acts:
      if a['canonical_smiles'] in selective:
        # Save ChEMBL Selective Compound tdl_info
        val = "{}|{}".format(a['chembl_id'], a['canonical_smiles'])
        rv = dba.ins_tdl_info( {'target_id': tid, 'itype': 'ChEMBL Selective Compound', 'string_value': val} )
        if rv:
          cscti_ct += 1
        else:
          dba_err_ct += 1
        break
  if not args['--quiet']:
    print(f"Inserted {cscti_ct} new 'ChEMBL Selective Compound' tdl_info rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")


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

  # ChEMBL MySQL connection
  f = open('/home/smathias/.dbirc', 'r')
  pw = f.readline().strip()
  f.close()
  chembldb = mysql.connector.connect(host='localhost', port=3306, db=CHEMBL_DB, user='smathias', passwd=pw)
  logger.info(f"Connected to ChEMBL database {CHEMBL_DB}")
  if not args['--quiet']:
    print(f"Connected to ChEMBL database {CHEMBL_DB}")

  start_time = time.time()

  # delete previous data, if any
  print("\nDeleting existing ChEMBL data...")
  rv = dba.del_cmpd_activities('ChEMBL')
  if type(rv) == int:
    print(f"  Deleted {rv} 'ChEMBL' cmpd_activity rows")
  else:
    print(f"Error deleting 'ChEMBL' cmpd_activity rows. See logfile {logfile} for details.")
    exit(1)
  rv = dba.del_dataset('ChEMBL')
  if not rv:
    print(f"Error deleting 'ChEMBL' dataset. See logfile {logfile} for details.")
    exit(1)
  rv = dba.del_tdl_infos('ChEMBL First Reference Year')
  if type(rv) == int:
    print(f"  Deleted {rv} 'ChEMBL First Reference Year' tdl_info rows")
  else:
    print(f"Error deleting 'ChEMBL First Reference Year' tdl_info rows. See logfile {logfile} for details.")
    exit(1)
  rv = dba.del_tdl_infos('ChEMBL Selective Compound')
  if type(rv) == int:
    print(f"  Deleted {rv} 'ChEMBL Selective Compound' tdl_info rows")
  else:
    print(f"Error deleting 'ChEMBL Selective Compound' tdl_info rows. See logfile {logfile} for details.")
    exit(1)
  rv = dba.del_dataset('ChEMBL Info')
  if not rv:
    print(f"Error deleteing 'ChEMBL Info' dataset. See logfile {logfile} for details.")
    exit(1)
    
  # First get mapping of UniProt accessions to ChEMBL IDs
  #download_mappings()
  up2chembl = {}
  fn = DOWNLOAD_DIR + UNIPROT2CHEMBL_FILE
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} input lines in mapping file {fn}")
  with open(fn, 'r') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    ct = 0
    for row in tsvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      if row[0].startswith('#'):
        continue
      if row[3] != 'SINGLE PROTEIN':
        continue
      if row[0] in up2chembl:
        up2chembl[row[0]].append(row[1])
      else:
        up2chembl[row[0]] = [row[1]]
  if not args['--quiet']:
    print("  Got {} UniProt to ChEMBL 'SINGLE PROTEIN' mappings".format(len(up2chembl)))

  # process and load new data
  load(args, dba, up2chembl, chembldb, logfile, logger)
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'ChEMBL', 'source': 'ChEMBL MySQL database {}'.format(CHEMBL_DB), 'app': PROGRAM, 'app_version': __version__, 'url': 'https://www.ebi.ac.uk/chembl/', 'comments': "The ChEMBL activities in TCRD are from two sources only: 'Scientific Literature' and 'Patent Bioactivity Data', and are also filtered for family-specific cutoffs."} )
  assert dataset_id, f"Error inserting ChEMBL dataset. See logfile {logfile} for details."
  dataset_id2 = dba.ins_dataset( {'name': 'ChEMBL Info', 'source': 'IDG-KMC generated data by Steve Mathias at UNM.', 'app': PROGRAM, 'app_version': __version__, 'comments': 'First reference year and selective compound info are generated by loader app.'} )
  assert dataset_id2, f"Error inserting ChEMBL Info dataset. See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'cmpd_acivity', 'where_clause': "catype = 'ChEMBL'"},
            {'dataset_id': dataset_id2, 'table_name': 'tdl_info', 'where_clause': "itype = 'ChEMBL First Reference Year'", 'comment': "Derived from filtered ChEMBL activities."},
            {'dataset_id': dataset_id2, 'table_name': 'tdl_info', 'where_clause': "itype = 'ChEMBL Selective Compound'", 'comment': "Derived from filtered ChEMBL activities."} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, "Error inserting provenance. See logfile {logfile} for details."
    
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))


