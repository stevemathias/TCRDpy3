#!/usr/bin/env python3
# Time-stamp: <2021-04-01 16:49:06 smathias>
"""
Load TIGA trait association data into TCRD from tab-delimited files.

Usage:
    load-TIGA.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-TIGA.py -h | --help

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
__version__   = "2.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
from urllib.request import urlretrieve
import gzip
import csv
from collections import defaultdict
import logging
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"
DOWNLOAD_DIR = '../data/TIGA/'
BASE_URL = 'https://unmtid-shinyapps.net/download/TIGA/'
TIGA_FILE = 'tiga_gene-trait_stats.tsv'
TIGA_PROV_FILE = 'tiga_gene-trait_provenance.tsv'

# def download(args):
#   for gzfn in [TIGA_FILE, TIGA_PROV_FILE]:
#     gzfp = DOWNLOAD_DIR + gzfn
#     fp = gzfp.replace('.gz', '')
#     if os.path.exists(gzfp):
#       os.remove(gzfp)
#     if os.path.exists(fp):
#       os.remove(fp)
#     if not args['--quiet']:
#       print "\nDownloading", BASE_URL + gzfn
#       print "         to", gzfp
#     urllib.urlretrieve(BASE_URL + gzfn, gzfp)
#     if not args['--quiet']:
#       print "Uncompressing", gzfp
#     ifh = gzip.open(gzfp, 'rb')
#     ofh = open(fp, 'wb')
#     ofh.write( ifh.read() )
#     ifh.close()
#     ofh.close()

def download():
  for fn in [TIGA_FILE, TIGA_PROV_FILE]:
    fp = DOWNLOAD_DIR + fn
    if os.path.exists(fp):
      os.remove(fp)
    print("\nDownloading {}".format(BASE_URL + fn))
    print("         to {}".format(fp))
    urlretrieve(BASE_URL + fn, fp)

def load(dba, logger, logfile):
  infile = DOWNLOAD_DIR + TIGA_FILE
  line_ct = slmf.wcl(infile)
  print(f"\nProcessing {line_ct} lines in TIGA file {infile}")
  ct = 0
  k2pids = defaultdict(list) # maps sym|ENSG to TCRD protein_id(s)
  notfnd = set()
  pmark = {}
  tiga_ct = 0
  dba_err_ct = 0
  with open(infile, 'r') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      # 0: ensemblId
      # 1: efoId
      # 2: trait
      # 3: n_study
      # 4: n_snp
      # 5: n_snpw
      # 6: geneNtrait
      # 7: geneNstudy
      # 8: traitNgene
      # 9: traitNstudy
      # 10: pvalue_mlog_median
      # 11: pvalue_mlog_max
      # 12: or_median
      # 13: n_beta
      # 14: study_N_mean
      # 15: rcras
      # 16: geneSymbol
      # 17: TDL
      # 18: geneFamily
      # 19: geneIdgList
      # 20: geneName
      # 21: meanRank
      # 22: meanRankScore
      ct += 1
      slmf.update_progress(ct/line_ct)
      sym = row[16]
      ensg = row[0]
      k = sym + '|' + ensg
      pids = []
      if k in k2pids:
        # we've already found it
        pids = k2pids[k]
      elif k in notfnd:
        # we've already not found it
        continue
      else:
        # look it up
        pids = dba.find_protein_ids({'sym': sym})
        if not pids:
          pids = dba.find_protein_ids_by_xref({'xtype': 'Ensembl', 'value': ensg})
          if not pids:
            notfnd.add(k)
            continue
        k2pids[k] = pids # save this mapping so we only lookup each sym/ENSG once
      init = {'ensg': ensg, 'efoid': row[1], 'trait': row[2], 'n_study': row[3], 'n_snp': row[4],
              'n_snpw': row[5], 'geneNtrait': row[6], 'geneNstudy': row[7], 'traitNgene': row[8],
              'traitNstudy': row[9], 'pvalue_mlog_median': row[10], 'pvalue_mlog_max': row[11],
              'n_beta': row[13], 'study_N_mean': row[14], 'rcras': row[15], 'meanRank': row[21],
              'meanRankScore': row[22]}
      if row[12] != 'NA':
        init['or_median'] = row[12]
      #if row[] != 'NA':
      #  init[''] = row[]
      for pid in pids:
        init['protein_id'] = pid
        rv = dba.ins_tiga(init)
        if not rv:
          dba_err_ct += 1
          continue
        tiga_ct += 1
        pmark[pid] = True
  for k in notfnd:
    logger.warn(f"No protein found for {k}")
  print(f"Processed {ct} lines")
  print("  Inserted {} new tiga rows for {} proteins".format(tiga_ct, len(pmark)))
  if notfnd:
    print("No target found for {} sym/ENSGs. See logfile {} for details.".format(len(notfnd), logfile))
  if dba_err_ct > 0:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

  infile = DOWNLOAD_DIR + TIGA_PROV_FILE
  line_ct = slmf.wcl(infile)
  print(f"\nProcessing {line_ct} lines in TIGA provenance file {infile}")
  ct = 0
  tigaprov_ct = 0
  dba_err_ct = 0
  with open(infile, 'r') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      # 0: ensemblId
      # 1: TRAIT_URI
      # 2: STUDY_ACCESSION
      # 3: PUBMEDID
      # 4: efoId
      ct += 1
      slmf.update_progress(ct/line_ct)
      rv = dba.ins_tiga_provenance( {'ensg': row[0], 'efoid': row[4],
                                     'study_acc': row[2], 'pubmedid': row[3]} )
      if not rv:
        dba_err_ct += 1
        continue
      tigaprov_ct += 1
  print(f"Processed {ct} lines")
  print(f"  Inserted {tigaprov_ct} new tiga_provenance rows")
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

  #download()
  start_time = time.time()
  load(dba, logger, logfile)
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'TIGA', 'source': f'TIGA Download files {TIGA_FILE} and {TIGA_PROV_FILE} from {BASE_URL}', 'app': PROGRAM, 'app_version': __version__, 'url': 'https://unmtid-shinyapps.net/shiny/tiga/'} )
  assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
  # Provenance
  provs = [ {'dataset_id': dataset_id, 'table_name': 'tiga'},
            {'dataset_id': dataset_id, 'table_name': 'tiga_provenance'} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
