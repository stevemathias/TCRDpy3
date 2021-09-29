#!/usr/bin/env python3
"""Load PubMed data into TCRD via EUtils.

Usage:
    load-PubMed.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-PubMed.py -h | --help

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
__email__     = "smathias@salud.unm.edu"
__org__       = "Translational Informatics Division, UNM School of Medicine"
__copyright__ = "Copyright 2015-2021, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "4.0.0"

import os,sys,time
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
import shelve
import slm_tcrd_functions as slmf
import tcrd_pubmed as tpm

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"
SHELF_FILE = f"{LOGDIR}/load-PubMed.db"

def load(args, dba, logger, logfile):
  s = shelve.open(SHELF_FILE, writeback=True)
  s['pids'] = [] # list of protein.ids that have been successfully processed
  s['pmids'] = [] # list of all stored pubmed ids
  s['p2p_ct'] = 0 # count of all stored protein2pubmed rows

  pids = dba.get_protein_ids()
  pct = len(pids)
  if not args['--quiet']:
    print(f"\nLoading pubmeds for {pct} TCRD proteins")
  logger.info(f"Loading pubmeds for {pct} TCRD proteins")

  for pid in pids:
    if pid in s['pids']:
      logger.info(f"Skipping previouslyprotein {}".format(pct))
      continue
  
  ct = 0
  dba_err_ct = 0
  if args['--pastid']:
    past_id = args['--pastid']
  else:
    past_id = 0
  for target in dba.get_targets(include_annotations=True, past_id=past_id):
    ct += 1
    logger.info("Processing target {}: {}".format(target['id'], target['name']))
    p = target['components']['protein'][0]
    if 'PubMed' not in p['xrefs']: continue
    pmids = [d['value'] for d in p['xrefs']['PubMed']]
    chunk_ct = 0
    err_ct = 0
    for chunk in slmf.chunker(pmids, 500):
      chunk_ct += 1
      r = get_pubmed(chunk)
      if not r or r.status_code != 200:
        # try again...
        r = get_pubmed(chunk)
        if not r or r.status_code != 200:
          logger.error("Bad E-Utils response for target {}, chunk {}".format(target['id'], chunk_ct))
          s['errors'][target['id']].append(chunk_ct)
          err_ct += 1
          continue
      soup = BeautifulSoup(r.text, "xml")
      pmas = soup.find('PubmedArticleSet')
      for pma in pmas.findAll('PubmedArticle'):
        pmid = pma.find('PMID').text
        if pmid not in s['pmids']: # only store each pubmed once
          logger.debug("  parsing XML for PMID: %s" % pmid)
          init = parse_pubmed_article(pma)
          rv = dba.ins_pubmed(init)
          if not rv:
            dba_err_ct += 1
            continue
          s['pmids'].append(pmid) # add pubmed id to list of saved ones
        rv = dba.ins_protein2pubmed({'protein_id': p['id'], 'pubmed_id': pmid})
        if not rv:
          dba_err_ct += 1
          continue
        s['p2p_ct'] += 1
      time.sleep(0.5)
    if err_ct == 0:
      s['loaded'].append(target['id'])
    pbar.update(ct)
  pbar.finish()
  print "Processed {} targets.".format(ct)
  print "  Successfully loaded all PubMeds for {} targets".format(len(s['loaded']))
  print "  Inserted {} new pubmed rows".format(len(s['pmids']))
  print "  Inserted {} new protein2pubmed rows".format(s['p2p_ct'])
  if dba_err_ct > 0:
    print "WARNING: {} DB errors occurred. See logfile {} for details.".format(dba_err_ct, logfile)
  if len(s['errors']) > 0:
    print "WARNING: {} Network/E-Utils errors occurred. See logfile {} for details.".format(len(s['errors']), logfile)

  loop = 1
  while len(s['errors']) > 0:
    print "\nRetry loop {}: Trying to load PubMeds for {} proteins".format(loop, len(s['errors']))
    logger.info("Retry loop {}: Trying to load data for {} proteins".format(loop, len(s['errors'])))
    pbar_widgets = ['Progress: ',Percentage(),' ',Bar(marker='#',left='[',right=']'),' ',ETA()]
    pbar = ProgressBar(widgets=pbar_widgets, maxval=len(s['errors'])).start()
    ct = 0
    dba_err_ct = 0
    for tid,chunk_cts in s['errors']:
      ct += 1
      target in dba.get_targets(tid, include_annotations=True)
      logger.info("Processing target {}: {}".format(target['id'], target['name']))
      p = target['components']['protein'][0]
      chunk_ct = 0
      err_ct = 0
      for chunk in chunker(pmids, 200):
        chunk_ct += 1
        # only process chunks that are in the errors lists
        if chunk_ct not in chunk_cts:
          continue
        r = get_pubmed(chunk)
        if not r or r.status_code != 200:
          # try again...
          r = get_pubmed(chunk)
          if not r or r.status_code != 200:
            logger.error("Bad E-Utils response for target {}, chunk {}".format(target['id'], chunk_ct))
            err_ct += 1
            continue
        soup = BeautifulSoup(r.text, "xml")
        pmas = soup.find('PubmedArticleSet')
        for pma in pmas.findAll('PubmedArticle'):
          pmid = pma.find('PMID').text
          if pmid not in s['pmids']:
            # only store each pubmed once
            logger.debug("  parsing XML for PMID: %s" % pmid)
            init = parse_pubmed_article(pma)
            rv = dba.ins_pubmed(init)
            if not rv:
              dba_err_ct += 1
              continue
            s['pmids'].append(pmid) # add pubmed id to list of saved ones
          rv = dba.ins_protein2pubmed({'protein_id': p['id'], 'pubmed_id': pmid})
          if not rv:
            dba_err_ct += 1
            continue
          s['p2p_ct'] += 1
        # remove chunk number from this target's error list
        s['errors'][tid].remove(chunk_ct)
        # it this target has no more errors, delete it from errors
        if len(s['errors'][tid]) == 0:
          del(s['errors'][tid])
        time.sleep(0.5)
      if err_ct == 0:
        s['loaded'].append(target['id'])
      pbar.update(ct)
    pbar.finish()
    print "Processed {} targets.".format(ct)
    print "  Successfully loaded all PubMeds for a total {} targets".format(len(s['loaded']))
    print "  Inserted {} new pubmed rows".format(len(s['pmids']))
    print "  Inserted {} new protein2pubmed rows".format(s['p2p_ct'])
    if dba_err_ct > 0:
      print "WARNING: {} DB errors occurred. See logfile {} for details.".format(dba_err_ct, logfile)
  if len(s['errors']) > 0:
    print "  {} targets remaining for next retry loop.".format(len(s['errors']))
  s.close()

  
if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  
  args = docopt(__doc__, version=__version__)
  if args['--debug']:
    print("\n[*DEBUG*] ARGS:\n{}\n".format(repr(args)))
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
  load(args, dba, logger, logfile)
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'PubMed', 'source': 'NCBI E-Utils', 'app': PROGRAM, 'app_version': __version__, 'url': 'https://www.ncbi.nlm.nih.gov/pubmed'} )
  assert dataset_id, "Error inserting dataset See logfile {} for details.".format(logfile)
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'pubmed'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'protein2pubmed'})
  assert rv, "Error inserting provenance. See logfile {} for details.".format(logfile)
  elapsed = time.time() - start_time

  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))




# Use this to manually insert errors
# In [26]: t = dba.get_target(18821, include_annotations=True)
# In [27]: p = target['components']['protein'][0]
# In [28]: pmids = [d['value'] for d in p['xrefs']['PubMed']]
# In [29]: len(pmids)
# Out[29]: 1387
# In [34]: url = EFETCHURL + ','.join(pmids[0:200])
# In [35]: r = requests.get(url)
# In [36]: r
# Out[36]: <Response [200]>
# In [43]: parse_insert(r)
# Inserted/Skipped 200 pubmed rows
# ct = 1
# for chunk in chunker(pmids, 200):
#   url = EFETCHURL + ','.join(pmids[0:200])
#   r = requests.get(url)
#   print "Chunk %d: %s" % (ct, r.status_code)
#   parse_insert(r)
# def parse_insert(r):
#   ct = 0
#   soup = BeautifulSoup(r.text, "xml")
#   pmas = soup.find('PubmedArticleSet')
#   for pma in pmas.findAll('PubmedArticle'):
#     pmid = pma.find('PMID').text
#     article = pma.find('Article')
#     title = article.find('ArticleTitle').text
#     init = {'id': pmid, 'protein_id': p['id'], 'title': title }
#     pd = article.find('PubDate')
#     if pd:
#       init['date'] = pubdate2isostr(pd)
#       abstract = article.find('AbstractText')
#     if abstract:
#       init['abstract'] = abstract.text
#     dba.ins_pubmed(init)
#     ct += 1
#   print "Inserted/Skipped %d pubmed rows" % ct

