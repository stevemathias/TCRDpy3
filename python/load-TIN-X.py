#!/usr/bin/env python3
# Time-stamp: <2021-04-21 14:47:41 smathias>
"""Load TIN-X data into TCRD from TSV files.

Usage:
    load-TIN-X.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-TIN-X.py -? | --help

Options:
  -h --dbhost DBHOST   : MySQL database host name [default: localhost]
  -n --dbname DBNAME   : MySQL database name [default: tcrdev]
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
__copyright__ = "Copyright 2015-2021, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "4.1.0"

import os,sys,time
from docopt import docopt
import mysql.connector
from mysql.connector import Error
import logging
import csv
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
# TIN-X TSV files (produced by tin-x.py):
INFILES = {'tinx_novelty': f"../data/TIN-X/TCRDv{TCRD_VER}/ProteinNovelty.tsv",
           'tinx_disease': f"../data/TIN-X/TCRDv{TCRD_VER}/DiseaseNovelty.tsv",
           'tinx_importance': f"../data/TIN-X/TCRDv{TCRD_VER}/Importance.tsv",
           'tinx_articlerank': f"../data/TIN-X/TCRDv{TCRD_VER}/PMIDRanking.tsv",
           'pubmed': f"../data/TIN-X/TCRDv{TCRD_VER}/TINX_Pubmed.tsv"}
# TIN-X table DDL
TABLES = {}
TABLES['tinx_novelty'] = (
  "CREATE TABLE `tinx_novelty` ("
  "`id` int(11) NOT NULL AUTO_INCREMENT,"
  "`protein_id` int(11) NOT NULL,"
  "`score` decimal(34,16) NOT NULL,"
  "PRIMARY KEY (`id`),"
  "KEY `tinx_novelty_idx1` (`protein_id`),"
  "CONSTRAINT `fk_tinx_novelty__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci")
TABLES['tinx_disease'] = (
  "CREATE TABLE `tinx_disease` ("
  "`doid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,"
  "`name` text COLLATE utf8_unicode_ci NOT NULL,"
  "`summary` text COLLATE utf8_unicode_ci,"
  "`score` decimal(34,16) DEFAULT NULL,"
  "PRIMARY KEY (`doid`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci")
TABLES['tinx_importance'] = (
  "CREATE TABLE `tinx_importance` ("
  "`doid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,"
  "`protein_id` int(11) NOT NULL,"
  "`score` decimal(34,16) NOT NULL,"
  "PRIMARY KEY (`doid`, `protein_id`),"
  "KEY `tinx_importance_idx1` (`protein_id`),"
  "KEY `tinx_importance_idx2` (`doid`),"
  "CONSTRAINT `fk_tinx_importance__tinx_disease` FOREIGN KEY (`doid`) REFERENCES `tinx_disease` (`doid`),"
  "CONSTRAINT `fk_tinx_importance__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci" )
TABLES['tinx_articlerank'] = (
  "CREATE TABLE `tinx_articlerank` ("
  "`id` int(11) NOT NULL AUTO_INCREMENT,"
  "`doid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,"
  "`protein_id` int(11) NOT NULL,"
  "`pmid` int(11) NOT NULL,"
  "`rank` int(11) NOT NULL,"
  "PRIMARY KEY (`id`),"
  "KEY `tinx_articlerank_idx1` (`doid`, `protein_id`),"
  "KEY `tinx_articlerank_idx2` (`pmid`)"
  ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci")
  #"CONSTRAINT `fk_tinx_articlerank__tinx_importance` FOREIGN KEY (`doid`, `protein_id`) REFERENCES `tinx_importance` (`doid`, `protein_id`)"
TABLES['tinx_target'] = (
  "CREATE VIEW tinx_target AS "
  "SELECT t.id target_id, p.id protein_id, p.uniprot, p.sym, t.tdl, t.fam, p.family "
  "FROM target t, t2tc, protein p "
  "WHERE t.id = t2tc.target_id AND t2tc.protein_id = p.id")
# INSERT statements
INS_SQL = {
  'tinx_novelty': "INSERT INTO tinx_novelty (protein_id, score) VALUES (%s, %s)",
  'tinx_disease': "INSERT INTO tinx_disease (doid, name, summary, score) VALUES (%s, %s, %s, %s)",
  'tinx_importance': "INSERT INTO tinx_importance (doid, protein_id, score) VALUES (%s, %s, %s)",
  'tinx_articlerank': "INSERT INTO tinx_articlerank (doid, protein_id, pmid, rank) VALUES (%s, %s, %s, %s)",
  'pubmed': "INSERT INTO pubmed (id, title, journal, date, authors, abstract) VALUES (%s, %s, %s, %s, %s, %s)",
  'dataset':"INSERT INTO dataset (name, source, app, app_version, comments) VALUES (%s, %s, %s, %s, %s)",
  'provenance': "INSERT INTO provenance (dataset_id, table_name, comment) VALUES (%s, %s, %s)",
  }

def drop_tables(curs):
  print('\nDropping old tinx tables: ', end='')
  curs.execute("DROP TABLE IF EXISTS tinx_articlerank")
  curs.execute("DROP TABLE IF EXISTS tinx_importance")
  curs.execute("DROP TABLE IF EXISTS tinx_disease")
  curs.execute("DROP TABLE IF EXISTS tinx_novelty")
  curs.execute("DROP VIEW IF EXISTS tinx_target")
  print("Done.")

def del_dataset(curs):
  print('\nDeleting old dataset/provenance (if any): ', end='')
  curs.execute("DELETE FROM provenance WHERE dataset_id = (SELECT id FROM dataset WHERE name = 'TIN-X Data')")
  curs.execute("DELETE FROM dataset WHERE name = 'TIN-X Data'")
  print("Done.")
  
def create_tables(curs):
  print('\nCreating new tinx tables: ', end='')
  for table in ['tinx_target', 'tinx_novelty', 'tinx_disease',
                'tinx_importance', 'tinx_articlerank']:
    curs.execute(TABLES[table])
  print("Done.")
  
def load_tinx(curs):
  chunk_size = 50000
  delim = '\t'
  print('\nLoading tinx tables...')
  for table in ['tinx_novelty', 'tinx_disease', 'tinx_importance', 'tinx_articlerank']:
    print(f"  Loading {table}: ", end='')
    fn = INFILES[table]
    st = time.time()
    first_chunk = True
    row_ct = 0
    for values in slmf.file_chunker(fn, chunk_size, delim):
      if first_chunk:
        values.pop(0) # get rid of the header
        first_chunk = False
      row_ct += len(values)
      curs.executemany(INS_SQL[table], [tuple(vals) for vals in values])
    ets = slmf.secs2str(time.time() - st)
    print(f"OK - ({row_ct} rows).  Elapsed time: {ets}")
  print("Done.")

def load_pubmed(curs, logger, logfile):
  st = time.time()
  fn = INFILES['pubmed']
  line_ct = slmf.wcl(fn)
  print(f'\nLoading TIN-X pubmeds from {fn}...')
  ct = 0
  pm_ct = 0
  dup_ct = 0
  err_ct = 0
  with open(fn, 'r') as ifh:
    tsvreader = csv.reader(ifh, delimiter='\t')
    for row in tsvreader:
      if ct == 0: # skip header
        header = row # header line
        ct += 1
        continue
      ct += 1
      slmf.update_progress(ct/line_ct)
      try:
        curs.execute(INS_SQL['pubmed'], tuple(row))
        pm_ct += 1
      except Error as e:
        if f"Duplicate entry '{row[0]}'" in e.msg:
          # this should not happen under "production" runs, but it's here for testing/debugging
          dup_ct += 1
          continue
        else:
          err_ct += 1
          logger.error(f"``{e}`` for line {ct}. Data: {row}")
          continue
  ets = slmf.secs2str(time.time() - st)
  print(f"\n  Processed {ct} lines. Inserted {pm_ct} pubmed rows. Elapsed time: {ets}")
  if err_ct:
    print(f"  WARNING: {err_ct} errors occurred. See logfile {logfile} for details.")
  if dup_ct:
    print(f"  Skipped {dup_ct} existing pubmeds.")
  print("Done.")
  
def load_dataset(curs):
  print('\nLoading dataset and provenance: ', end='')
  dataset_data = ('TIN-X Data', 'IDG-KMC generated data by Steve Mathias at UNM.', PROGRAM, __version__, 'TIN-X scores and articl ranks are generated using files human_textmining_mentions.tsv and disease_textmining_mentions.tsv from http://download.jensenlab.org/.')
  curs.execute(INS_SQL['dataset'], dataset_data)
  dataset_id = curs.lastrowid
  provenance_data = [ (dataset_id, 'tinx_novelty', "Protein novelty scores are generated from results of JensenLab textmining of PubMed in the file http://download.jensenlab.org/human_textmining_mentions.tsv. To calculate novelty scores, each paper (PMID) is assigned a fractional target (FT) score of one divided by the number of targets mentioned in it. The novelty score of a given protein is one divided by the sum of the FT scores for all the papers mentioning that protein."),
            (dataset_id, 'tinx_disease', "Disease novelty scores are generated from results of JensenLab textmining of PubMed in the file http://download.jensenlab.org/disease_textmining_mentions.tsv. To calculate novelty scores, each paper (PMID) is assigned a fractional disease (FD) score of one divided by the number of targets mentioned in it. The novelty score of a given disease is one divided by the sum of the FT scores for all the papers mentioning that disease."),
            (dataset_id, 'tinx_importance', "To calculate importance scores, each paper is assigned a fractional disease-target (FDT) score of one divided by the product of the number of targets mentioned and the number of diseases mentioned. The importance score for a given disease-target pair is the sum of the FDT scores for all papers mentioning that disease and protein."),
            (dataset_id, 'tinx_articlerank', "PMIDs are ranked for a given disease-target pair based on a score calculated by multiplying the number of targets mentioned and the number of diseases mentioned in that paper. Lower scores have a lower rank (higher priority). If the scores do not discriminate, PMIDs are reverse sorted by value with the assumption that larger PMIDs are newer and of higher priority.") ]
  for pd in provenance_data:
    curs.execute(INS_SQL['provenance'], pd)
  print("Done.")


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
  
  st = time.time()
  cnx = None
  try:
    cnx = mysql.connector.connect(host = args['--dbhost'],
                                  database = args['--dbname'],
                                  user = 'smathias',
                                  password = slmf.get_pw('/home/smathias/.dbirc'),
                                  autocommit = True)
    if cnx.is_connected():
      if not args['--quiet']:
        print("Connected to TCRD database {}".format(args['--dbname']))
      curs = cnx.cursor()
      del_dataset(curs)
      drop_tables(curs)
      create_tables(curs)
      load_tinx(curs)
      load_pubmed(curs, logger, logfile)
      load_dataset(curs)
      curs.close()
  except Error as e:
    print(f"ERROR: {e}")
  finally:
    if cnx and cnx.is_connected():
      cnx.commit()
      cnx.close()
  ets = slmf.secs2str(time.time() - st)
  print(f"\n{PROGRAM}: Done. Total time: {ets}\n")
