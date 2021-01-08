#!/usr/bin/env python3
# Time-stamp: <2021-01-07 11:59:32 smathias>
"""Update JensenLab resources and dependent data in TCRD.

Usage:
    update-JensenLab.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    update-JensenLab -? | --help

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
__copyright__ = "Copyright 2020, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "1.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
from TINX import TINX
from urllib.request import urlretrieve
import obo
import csv
import logging
import obo
from functools import cmp_to_key
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS !!! ##
#LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGDIR = f"./tcrd{TCRD_VER}logs"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"

JL_BASE_URL = 'http://download.jensenlab.org/'
JL_DOWNLOAD_DIR = '../data/JensenLab/'
PM_SCORES_FILE = 'protein_counts.tsv' # in KMC/Medline dir on server
DISEASES_FILE_K = 'human_disease_knowledge_filtered.tsv'
DISEASES_FILE_E = 'human_disease_experiments_filtered.tsv'
DISEASES_FILE_T = 'human_disease_textmining_filtered.tsv'
TINX_DISEASE_FILE = 'disease_textmining_mentions.tsv'
TINX_PROTEIN_FILE = 'human_textmining_mentions.tsv'
DO_BASE_URL = 'https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/'
DO_DOWNLOAD_DIR = '../data/DiseaseOntology/'
DO_OBO = 'doid.obo'
# Directory for TIN-X CSV files
TINX_OUTDIR = f"../data/TIN-X/TCRDv{TCRD_VER}/"

def download_pmscores(args):
  if os.path.exists(DOWNLOAD_DIR + PM_SCORES_FILE):
    os.remove(DOWNLOAD_DIR + PM_SCORES_FILE)
  if not args['--quiet']:
    print(f"\nDownloading {BASE_URL}KMC/Medline/{PM_SCORES_FILE}")
    print(f"         to {DOWNLOAD_DIR}{PM_SCORES_FILE}")
  urllib.urlretrieve(f"{BASE_URL}KMC/Medline/{PM_SCORES_FILE}", DOWNLOAD_DIR + PM_SCORES_FILE)

def download_DISEASES(args):
  for fn in [DISEASES_FILE_K, DISEASES_FILE_E, DISEASES_FILE_T]:
    if os.path.exists(JL_DOWNLOAD_DIR + fn):
      os.remove(JL_DOWNLOAD_DIR + fn)
    if not args['--quiet']:
      print("\nDownloading {}".format(JL_BASE_URL + fn))
      print("         to {}".format(JL_DOWNLOAD_DIR + fn))
    urlretrieve(JL_BASE_URL + fn, JL_DOWNLOAD_DIR + fn)
  
def download_mentions(args):
  for fn in [TINX_DISEASE_FILE, TINX_PROTEIN_FILE]:
    if os.path.exists(JL_DOWNLOAD_DIR + fn):
      os.remove(JL_DOWNLOAD_DIR + fn)
    if not args['--quiet']:
      print("\nDownloading {}".format(JL_BASE_URL + fn))
      print("         to {}".format(JL_DOWNLOAD_DIR + fn))
    urlretrieve(JL_BASE_URL + fn, JL_DOWNLOAD_DIR + fn)

def download_do(args):
  if os.path.exists(DO_DOWNLOAD_DIR + DO_OBO):
    os.remove(DO_DOWNLOAD_DIR + DO_OBO)
  if not args['--quiet']:
      print("\nDownloading {}".format(DO_BASE_URL + DO_OBO))
      print("         to {}".format(DO_DOWNLOAD_DIR + DO_OBO))
  urlretrieve(DO_BASE_URL + DO_OBO, DO_DOWNLOAD_DIR + DO_OBO)

def load_pmscores(args, dba, logger, logfile):
  ensp2pids = {} # ENSP => list of TCRD protein ids
  pmscores = {} # protein.id => sum(all scores)
  pms_ct = 0
  skip_ct = 0
  notfnd = set()
  dba_err_ct = 0
  infile = DOWNLOAD_DIR + PM_SCORES_FILE
  line_ct = slmf.wcl(infile)
  if not args['--quiet']:
    print(f"\nProcessing {line_ct} lines in file {infile}")
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
  if notfnd:
    print("No protein found for {} STRING IDs. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  print("\nLoading {} JensenLab PubMed Score tdl_infos".format(len(pmscores)))
  ct = 0
  ti_ct = 0
  dba_err_ct = 0
  for pid,score in pmscores.items():
    ct += 1
    rv = dba.ins_tdl_info({'protein_id': pid, 'itype': 'JensenLab PubMed Score', 
                           'number_value': score} )
    if rv:
      ti_ct += 1
    else:
      dba_err_ct += 1
  print(f"{ct} processed")
  print(f"  Inserted {ti_ct} new JensenLab PubMed Score tdl_info rows")
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

def load_DISEASES(args, dba, logger, logfile):
  # Knowledge channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_K
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print(f"Processing {line_ct} lines in DISEASES Knowledge file {fn}")
  with open(fn, 'r') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
    ct = 0
    k2pids = {} # ENSP|sym => list of TCRD protein ids
    pmark = {}
    notfnd = set()
    dis_ct = 0
    dba_err_ct = 0
    for row in tsvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      ensp = row[0]
      sym = row[1]
      k = "%s|%s"%(ensp,sym)
      if k in k2pids:
        # we've already found it
        pids = k2pids[k]
      elif k in notfnd:
        # we've already not found it
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
  print("Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print("WARNING: {} DB errors occurred. See logfile {} for details.".format(dba_err_ct, logfile))
    
  # Experiment channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_E
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print(f"Processing {line_ct} lines in DISEASES Experiment file {fn}")
  with open(fn, 'rU') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
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
      if float(row[6]) < 3.0:
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
  print("Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows with confidence < 3")
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print("WARNING: {} DB errors occurred. See logfile {} for details.".format(dba_err_ct, logfile))

  # Text Mining channel
  fn = JL_DOWNLOAD_DIR + DISEASES_FILE_T
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print(f"Processing {line_ct} lines in DISEASES Textmining file {fn}")
  pbar_widgets = ['Progress: ',Percentage(),' ',Bar(marker='#',left='[',right=']'),' ',ETA()]
  pbar = ProgressBar(widgets=pbar_widgets, maxval=line_ct).start() 
  with open(fn, 'rU') as tsv:
    tsvreader = csv.reader(tsv, delimiter='\t')
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
      if float(row[6]) < 3.0:
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
  print("Inserted {} new disease rows for {} proteins".format(dis_ct, len(pmark)))
  if skip_ct:
    print(f"  Skipped {skip_ct} rows with confidence < 3")
  if notfnd:
    print("  No target found for {} stringids/symbols. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print("WARNING: {} DB errors occurred. See logfile {} for details.".format(dba_err_ct, logfile))

def load_tinx(args, dba, do, logger, logfile):
  fn = f"{TINX_OUTDIR}ProteinNovelty.csv"
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print("f\nProcessing {line_ct} lines in file {fn}")
  with open(fn, 'rU') as csvfile:
    csvreader = csv.reader(csvfile)
    header = csvreader.next() # skip header line
    # Protein ID,UniProt,Novelty
    ct = 1
    tn_ct = 0
    dba_err_ct = 0
    for row in csvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      pid = row[0]
      rv = dba.ins_tinx_novelty( {'protein_id': pid, 'score': float(row[2])} )
      if rv:
        tn_ct += 1
      else:
        dba_err_ct += 1
  print(f"{ct} input lines processed.")
  print("  Inserted {tnct} new tinx_novelty rows".)
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")
  
  dmap = {}
  fn = f"{TINX_OUTDIR}DiseaseNovelty.csv"
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print("f\nProcessing {line_ct} lines in file {fn}")
  with open(fn, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = csvreader.next() # skip header line
    # DOID,Novelty
    ct = 1
    dct = 0
    notfnd = set()
    dba_err_ct = 0
    for row in csvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      doid = row[0]
      if doid in do:
        if 'name' in do[doid]:
          dname = do[doid]['name'][0].value
        else:
          continue
        if 'def' in do[doid]:
          ddef = do[doid]['def'][0].value
        else:
          ddef = None
      else:
        logger.warn("{row[0]} not in DO map")
        notfnd.append(row[0])
        continue
      rv = dba.ins_tinx_disease( {'doid': doid, 'name': dname, 
                                  'summary': ddef, 'score': float(row[1])} )
      if rv:
        dct += 1
        dmap[doid] = rv # map DOID to tinx_disease.id
      else:
        dba_err_ct += 1
  print(f"{ct} input lines processed.")
  print("  Inserted {dct} new tinx_disease rows".)
  print("  Saved {} keys in dmap".format(len(dmap)))
  if notfnd:
    print("WARNNING: No entry found in DO map for {} DOIDs. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

  imap = {}
  fn = f"{TINX_OUTDIR}Importance.csv"
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print("f\nProcessing {line_ct} lines in file {fn}")
  with open(fn, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    header = csvreader.next() # skip header line
    # DOID,Protein ID,UniProt,Score
    ct = 1
    ti_ct = 0
    skips1 = set()
    dba_err_ct = 0
    for row in csvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      if row[0] not in dmap:
        logger.warn("{row[0]} not in dmap")
        skips1.add(row[0])
        continue
      did = dmap[row[0]]
      pid = row[1]
      rv = dba.ins_tinx_importance( {'protein_id': pid, 'disease_id': did,
                                     'score': float(row[3])} )
      if rv:
        ti_ct += 1
        # map DOID|PID to tinx_importance.id
        k = f"{row[0]}|{row[1]}"
        imap[k] = rv 
      else:
        dba_err_ct += 1
  print(f"{ct} input lines processed.")
  print("  Inserted {ti_ct} new tinx_importance rows".)
  print("  Saved {} keys in imap".format(len(imap)))
  if len(skips1) > 0:
    print("WARNNING: No disease found in dmap for {} DOIDs. See logfile {} for details.".format(len(skips1), logfile))
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")

  fn = f"{TINX_OUTDIR}PMIDRanking.csv"
  line_ct = slmf.wcl(fn)
  if not args['--quiet']:
    print("f\nProcessing {line_ct} lines in file {fn}")
  regex = re.compile(r"^DOID:0*")
  with open(fn, 'rU') as csvfile:
    csvreader = csv.reader(csvfile)
    header = csvreader.next() # skip header line
    # DOID,Protein ID,UniProt,PubMed ID,Rank
    ct = 1
    tar_ct = 0
    skips = set()
    dba_err_ct = 0
    for row in csvreader:
      ct += 1
      slmf.update_progress(ct/line_ct)
      k = "%s|%s"%(row[0],row[1])
      if k not in imap:
        logger.warn("{k} not in imap")
        skips.add(k)
        continue
      iid = imap[k]
      rv = dba.ins_tinx_articlerank( {'importance_id': iid, 'pmid': row[3], 'rank': row[4]} )
      if rv:
        tar_ct += 1
      else:
        dba_err_ct += 1
  print(f"{ct} input lines processed.")
  print("  Inserted {tar_ct} new tinx_articlerank rows".)
  if len(skips) > 0:
    print("WARNNING: No importance found in imap for {} keys. See logfile {} for details.".format(len(skips), logfile))
  if dba_err_ct > 0:
    print(f"WARNING: {db_err_ct} DB errors occurred. See logfile {logfile} for details.")


if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  
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

  print("\nDownloading update files...")
  download_pmscores(args)
  download_DISEASES(args)
  download_mentions(args)
  download_do(args)

  start_time = time.time()
  print("\nUpdating JensenLab PubMed Text-mining Scores...")
  # delete existing pmscores
  rv = dba.del_all_rows(pmscore)
  if type(rv) == int:
    print(f"  Deleted {rv} rows from pmscore")
  else:
    print(f"Error deleting rows from pmscore... Exiting.")
    exit(1)
  # delete 'JensenLab PubMed Score' TDL Infos
  rv = dba.del_tdl_infos('JensenLab PubMed Score')
  if type(rv) == int:
    print(f"  Deleted {rv} 'JensenLab PubMed Score' tdl_info rows")
  else:
    print(f"Error deleting 'JensenLab PubMed Score' tdl_info rows. Exiting.")
    exit(1)
  # load new pmsores and TDL Infos
  load_pmscores(args, dba, logger, logfile)
  # update dataset
  upds = {'app': PROGRAM, 'app_version': __version__,
          'datetime': time.strftime("%Y-%m-%d %H:%M:%S")}
  rv = upd_dataset_by_name(self, 'JensenLab PubMed Text-mining Scores', upds):
  assert rv "Error updating dataset 'JensenLab PubMed Text-mining Scores'. Exiting."

  print("\nUpdating JensenLab DISEASES...")
  # delete existing DISEASES
  rv = dba.del_jldiseases()
  if type(rv) == int:
    print(f"Deleted {rv} JensenLab rows from disease")
  else:
    print(f"Error deleting JensenLab rows from disease... Exiting.")
    exit(1)
  # load new DISEAESES
  load_DISEASES(args, dba, logger, logfile)
  # update dataset
  upds = {'app': PROGRAM, 'app_version': __version__,
          'datetime': time.strftime("%Y-%m-%d %H:%M:%S")}
  rv = upd_dataset_by_name(self, 'Jensen Lab DISEASES', upds):
  assert rv "Error updating dataset 'Jensen Lab DISEASES'. Exiting."

  print("\Generating new TIN-X Files...")
  # parse the Disease Ontology OBO file to get DO names and defs
  dofile = DO_DOWNLOAD_DIR+DO_OBO
  if not args['--quiet']:
    print(f"\nParsing Disease Ontology file {dofile}")
  do_parser = obo.Parser(dofile)
  do = {}
  for stanza in do_parser:
    do[stanza.tags['id'][0].value] = stanza.tags
  if not args['--quiet']:
    print("  Got {} Disease Ontology terms".format(len(do)))
  tinx_logfile = LOGDIR+'TINX.log'
  tinx = TINX({'TINX_PROTEIN_FILE': DOWNLOAD_DIR+TINX_PROTEIN_FILE,
               'TINX_DISEASE_FILE': DOWNLOAD_DIR+TINX_DISEASE_FILE,
               'logfile': tinx_logfile, 'OUTDIR': TINX_OUTDIR}, dba, do)
  (ct1, ct2) = tinx.parse_protein_mentions()
  if not args['--quiet']:
    print(f"Saved {ct1} protein to PMIDs mappings and {ct2} PMID to protein count mappings. See logfile {tinx_logfile} for details.")
  (ct1, ct2) = tinx.parse_disease_mentions()
  if not args['--quiet']:
    print(f"Saved {ct1} disease to PMIDs mappings and {ct2} PMID to disease count mappings. See logfile {tinx_logfile} for details.")
  (ct, fn) = tinx.compute_protein_novelty()
  if not args['--quiet']:
    print(f"{ct} protein novelty rows written to file {fn}. See logfile {tinx_logfile} for details.")
  (ct, fn) = tinx.compute_disease_novelty()
  if not args['--quiet']:
    print(f"{ct} disease novelty rows written to file {fn}. See logfile {tinx_logfile} for details.")
  (ct, fn) = tinx.compute_importances()
  if not args['--quiet']:
    print(f"{ct} importance scores written to file {fn}. See logfile {tinx_logfile} for details.")
  (ct, fn) = tinx.compute_pubmed_rankings()
  if not args['--quiet']:
    print(f"{ct} PubMed rankings written to file {fn}. See logfile {tinx_logfile} for details.")

  print("\nUpdating TIN-X...")
  # delete existing tinx data
  rv = dba.del_all_rows('tinx_articlerank')
  rv = dba.del_all_rows('tinx_importance')
  rv = dba.del_all_rows('tinx_disease')
  rv = dba.del_all_rows('tinx_novelty')
  # load new TIN-X data
  load_tinx(args, dba, do, logger, logfile)
  # update dataset
  upds = {'app': PROGRAM, 'app_version': __version__,
          'datetime': time.strftime("%Y-%m-%d %H:%M:%S")}
  rv = upd_dataset_by_name(self, 'TIN-X Data', upds):
  assert rv "Error updating dataset 'TIN-X Data'. Exiting."
  
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
