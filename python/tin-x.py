#!/usr/bin/env python3
# Time-stamp: <2022-09-06 14:26:45 smathias>
"""Generate TIN-X TSV files with scores and PubMed ID rankings from Jensen Lab's protein and disease mentions TSV files.

Usage:
    TIN-X.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    TIN-X.py -? | --help

Options:
  -h --dbhost DBHOST   : MySQL database host name [default: localhost]
  -n --dbname DBNAME   : MySQL database name [default: tcrd]
  -l --logfile LOGF    : set log file name
  -v --loglevel LOGL   : set logging level [default: 20]
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
__copyright__ = "Copyright 2016-2022, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "5.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
from TINX import TINX
import requests
import logging
import obo
import slm_util_functions as slmf
import tcrd_pubmed as tpm

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"

DO_BASE_URL = 'https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/master/src/ontology/'
DO_DOWNLOAD_DIR = '../data/DiseaseOntology/'
DO_OBO = 'doid.obo'
JL_BASE_URL = 'http://download.jensenlab.org/'
JL_DOWNLOAD_DIR = '../data/JensenLab/'
TINX_DISEASE_FILE = 'disease_textmining_mentions.tsv'
TINX_PROTEIN_FILE = 'human_textmining_mentions.tsv'
# Directory for output TSV files
TINX_OUTDIR = f"../data/TIN-X/TCRDv{TCRD_VER}/"

def download_do(args):
  if os.path.exists(DO_DOWNLOAD_DIR + DO_OBO):
    os.remove(DO_DOWNLOAD_DIR + DO_OBO)
  if not args['--quiet']:
      print("\nDownloading {}".format(DO_BASE_URL + DO_OBO))
      print("         to {}".format(DO_DOWNLOAD_DIR + DO_OBO))
  urlretrieve(DO_BASE_URL + DO_OBO, DO_DOWNLOAD_DIR + DO_OBO)

def download_mentions(args):
  for fn in [TINX_DISEASE_FILE, TINX_PROTEIN_FILE]:
    if os.path.exists(JL_DOWNLOAD_DIR + fn):
      os.remove(JL_DOWNLOAD_DIR + fn)
    if not args['--quiet']:
      print("\nDownloading {}".format(JL_BASE_URL + fn))
      print("         to {}".format(JL_DOWNLOAD_DIR + fn))
    urlretrieve(JL_BASE_URL + fn, JL_DOWNLOAD_DIR + fn)

def parse_do(args, dofile):
  if not args['--quiet']:
    print(f"\nParsing Disease Ontology file {dofile}")
  do_parser = obo.Parser(dofile)
  do = {}
  for stanza in do_parser:
    do[stanza.tags['id'][0].value] = stanza.tags
  if not args['--quiet']:
    print("  Got {} Disease Ontology terms".format(len(do)))
  return do
    
def do_tinx(args, dba, do, logger, logfile):
  tinx = TINX({'TINX_PROTEIN_FILE': JL_DOWNLOAD_DIR+TINX_PROTEIN_FILE,
               'TINX_DISEASE_FILE': JL_DOWNLOAD_DIR+TINX_DISEASE_FILE,
               'logfile': logfile, 'OUTDIR': TINX_OUTDIR}, dba, do)
  st = time.time()
  (ct1, ct2) = tinx.parse_protein_mentions()
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Protein mappings: {ct1} protein to PMIDs ; {ct2} PMID to protein counts. Elapsed time: {ets}")
  st = time.time()
  (ct1, ct2) = tinx.parse_disease_mentions()
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Disease mappings: {ct1} disease to PMIDs ; {ct2} PMID to disease counts. Elapsed time: {ets}")
  st = time.time()
  (ct, fn) = tinx.compute_protein_novelty()
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Wrote {ct} lines to file {fn}. Elapsed time: {ets}")
  st = time.time()
  (ct, fn) = tinx.compute_disease_novelty()
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Wrote {ct} lines to file {fn}. Elapsed time: {ets}")
  st = time.time()
  (ct, fn) = tinx.compute_importances()
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Wrote {ct} lines to file {fn}. Elapsed time: {ets}")
  st = time.time()
  (ct, tinx_pmids, fn) = tinx.compute_pubmed_rankings()
  tinx_pmid_ct = len(tinx_pmids)
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"Wrote {ct} lines ({tinx_pmid_ct} total TIN-x PMIDs) to file {fn}. Elapsed time: {ets}")
  return tinx_pmids
    
def tinx_pubmed(args, dba, tinx_pmids, logger):
  st = time.time()
  tcrd_pmids = set(dba.get_pmids())
  new_pmids = tinx_pmids - tcrd_pmids
  new_pmids = [str(i) for i in list(new_pmids)]
  new_pmid_ct = len(new_pmids)
  if not args['--quiet']:
    print(f"Fetching pubmed data for {new_pmid_ct} new TIN-X PMIDs")
  logger.info(f"Fetching pubmed data for {new_pmid_ct} new TIN-X PMIDs")
  ct = 0
  net_err_ct = 0
  chunk_ct = 0
  fn = f"{TINX_OUTDIR}TINX_Pubmed.tsv"
  with open(fn, 'w') as ofh:
    ofh.write("PubMedID\tTitle\tJournal\tDate\tAutors\tAbstract\n")
    ct += 1
    for chunk in slmf.chunker(new_pmids, 200):
      chunk_ct += 1
      logger.info(f"Processing PMID chunk {chunk_ct}")
      pmas = tpm.fetch_pubmeds(chunk)
      if not pmas:
        logger.error("Bad E-Utils response for PMID chunk {}: {}".format(chunk_ct, ','.join(chunk)))
        net_err_ct += 1
        continue
      for pma in pmas:
        pmid, title, journal, date, authors, abstract = tpm.parse_pubmed_article(pma)
        if abstract:
          ofh.write(f"{pmid}\t{title}\t{journal}\t{date}\t{authors}\t{abstract}\n")
        else:
          ofh.write(f"{pmid}\t{title}\t{journal}\t{date}\t{authors}\t''\n")
        ct += 1
  ets = slmf.secs2str(time.time() - st)
  if not args['--quiet']:
    print(f"{ct} lines written to file {fn}. Elapsed time: {ets}")
  if net_err_ct > 0:
    print(f"WARNING: {net_err_ct} Network/E-Utils errors occurred.")


if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  
  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print(f"\n[*DEBUG*] ARGS:\n{args}\n")
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
  logger.info(f"Connected to TCRD database {args['--dbname']} (schema ver {dbi['schema_ver']}; data ver {dbi['data_ver']})")
  if not args['--quiet']:
    print(f"Connected to TCRD database {args['--dbname']} (schema ver {dbi['schema_ver']}; data ver {dbi['data_ver']})")

  st = time.time()
  #download_do(args)
  download_mentions(args)
  do = parse_do(args, DO_DOWNLOAD_DIR+DO_OBO) # get DO names and defs
  print(f"\nGenerating TIN-X TSV files. See logfile {logfile} for details.\n")
  tinx_pmids = do_tinx(args, dba, do, logger, logfile)
  tinx_pubmed(args, dba, tinx_pmids, logger)
  ets = slmf.secs2str(time.time() - st)
  print(f"\n{PROGRAM}: Done. Total time: {ets}\n")
  
