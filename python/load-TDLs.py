#!/usr/bin/env python
# Time-stamp: <2021-05-06 13:50:10 smathias>
"""Calculate and load target TDL assignments, and also export an new UniProt mapping file.

Usage:
    load-TDLs.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-TDLs.py | --help

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
__version__   = "4.2.0"

import os,sys,time,shutil
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '6' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}{PROGRAM}.log"
OUTDIR = '/usr/local/apache2/htdocs/tcrd/download/old_versions/'
OUTFILE_PAT = OUTDIR + 'PharosTCRDv{}_UniProt_Mapping.tsv'
#OUTFILE = f'{OUTDIR}PharosTCRD_UniProt_Mapping.tsv'

def export_uniprot_mapping(dba, ofn):
  uptdls = dba.get_uniprots_tdls()
  ct = len(uptdls)
  exp_ct = 0
  print(f"\nExporting UniProts/TDLs for {ct} TCRD targets")
  with open(ofn, 'w') as ofh:
    ofh.write(f"UniProt_accession\tPharos_target\tTDL\n")
    for d in uptdls:
      ofh.write(f"{d['uniprot']}\t{d['uniprot']}\t{d['tdl']}\n")
      exp_ct += 1
      slmf.update_progress(exp_ct/ct)
  print(f"Wrote {exp_ct} lines to file {ofn}")

def load_tdls(dba, logfile, logger):
  tids = dba.get_target_ids()
  tct = len(tids)
  print(f"\nCalculating/Loading TDLs for {tct} TCRD targets")
  ct = 0
  tdl_cts = {'Tclin': 0, 'Tchem': 0, 'Tbio': 0, 'Tdark': 0}
  bump_ct = 0
  dba_err_ct = 0
  upd_ct = 0
  for tid in tids:
    tinfo = dba.get_target4tdlcalc(tid)
    ct += 1
    slmf.update_progress(ct/tct)
    (tdl, bump_flag) = compute_tdl(tinfo)
    tdl_cts[tdl] += 1
    if bump_flag:
      bump_ct += 1
    rv = dba.do_update({'table': 'target', 'id': tid, 'col': 'tdl', 'val': tdl})
    if rv:
      upd_ct += 1
    else:
      dba_err_ct += 1
  print(f"{ct} TCRD targets processed.")
  print(f"Set TDL value for {upd_ct} targets:")
  print("  {} targets are Tclin".format(tdl_cts['Tclin']))
  print("  {} targets are Tchem".format(tdl_cts['Tchem']))
  print("  {} targets are Tbio - {} bumped from Tdark".format(tdl_cts['Tbio'], bump_ct))
  print("  {} targets are Tdark".format(tdl_cts['Tdark']))
  if dba_err_ct:
    print(f"ERROR: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

def compute_tdl(tinfo):
  '''
  Input is a dictionary of target info, as returned by get_target4tdlcalc()
  Returns (tdl, bump_flag)
  '''
  bump_flag = False
  if 'drug_activities' in tinfo:
    if len([a for a in tinfo['drug_activities'] if a['has_moa'] == 1]) > 0:
      # MoA drug activities qualify a target as Tclin
      tdl = 'Tclin'
    else:
      # Non-MoA drug activities qualify a target as Tchem
      tdl = 'Tchem'
  elif 'cmpd_activities' in tinfo:
    # cmpd activities qualify a target as Tchem
    tdl = 'Tchem'
  else:
    # Collect info needed to decide between Tbio and Tdark
    p = tinfo['components']['protein'][0]
    ptdlis = p['tdl_infos']
    # JensenLab PubMed Score
    pms = float(ptdlis['JensenLab PubMed Score']['value'])
    # GeneRIF Count
    rif_ct = 0
    if 'generifs' in p:
      rif_ct = len(p['generifs'])
    # Ab Count
    ab_ct = int(ptdlis['Ab Count']['value']) 
    # Experimental MF/BP Leaf Term GOA
    efl_goa = False
    if 'Experimental MF/BP Leaf Term GOA' in ptdlis:
      efl_goa = True
    # # OMIM Phenotype
    # omim = False
    # if 'phenotypes' in p and len([d for d in p['phenotypes'] if d['ptype'] == 'OMIM']) > 0:
    #   omim = True
    # Decide between Tbio and Tdark
    dark_pts = 0    
    if pms < 5:     # PubMed Score < 5
      dark_pts += 1
    if rif_ct <= 3: # GeneRIF Count <= 3
      dark_pts += 1
    if ab_ct <= 50: # Ab Count <= 50
      dark_pts += 1
    if dark_pts >= 2:
      # if at least 2 of the above, target is Tdark...
      tdl = 'Tdark'
      if efl_goa:
        # ...unless target has Experimental MF/BP Leaf Term GOA, then bump to Tbio
        tdl = 'Tbio'
        bump_flag = True
    else:
      tdl = 'Tbio'
  return (tdl, bump_flag)


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

  rv = dba.upd_tdls_null()
  if type(rv) == int:
    print(f"\nSet tdl to NULL for {rv} target rows")
  else:
    print(f"Error setting target.tdl values to NULL. See logfile {logfile} for details.")
    exit(1)
  rv = dba.del_dataset('TDLs')
  if rv:
    print(f"\nDeleted previous 'TDLs' dataset")
  else:
    print(f"Error deleting 'TDLs' dataset. See logfile {logfile} for details.")
    exit(1)
  
  load_tdls(dba, logfile, logger)
  
  # Dataset
  dataset_id = dba.ins_dataset( {'name': 'TDLs', 'source': 'IDG-KMC generated data by Steve Mathias at UNM.', 'app': PROGRAM, 'app_version': __version__, 'comments': 'TDLs are calculated by the loading app from data in TCRD.'} )
  assert dataset_id, f"Error inserting dataset. See logfile {logfile} for details."
  # Provenance
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'tdl'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."

  # Add version number to filename and archive mapping file to old_versions dir
  mmver = '.'.join( dbi['data_ver'].split('.')[:2] )
  outfn = OUTFILE_PAT.format(mmver)
  export_uniprot_mapping(dba, outfn)
  #shutil.copy(outfn, '/usr/local/apache2/htdocs/tcrd/download/PharosTCRD_UniProt_Mapping.tsv')
  
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
