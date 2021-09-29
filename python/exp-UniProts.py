#!/usr/bin/env python3
# Time-stamp: <2021-04-22 12:25:38 smathias>
'''
exp-UniProts.py - 
'''
__author__ = "Steve Mathias"
__email__ = "smathias@salud.unm.edu"
__org__ = "Translational Informatics Division, UNM School of Medicine"
__copyright__ = "Copyright 2021, Steve Mathias"
__license__ = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__ = "1.1.0"

import os,sys,shutil,time
from TCRD.DBAdaptor import DBAdaptor
import slm_util_functions as slmf

PROGRAM = os.path.basename(sys.argv[0])
DBNAME = 'tcrd'
OUTDIR = '/usr/local/apache2/htdocs/tcrd/download/'
OUTFILE = f'{OUTDIR}PharosTCRD_UniProt_Mapping.tsv'
ARCHIVE_FILEPAT = OUTDIR + 'old_versions/PharosTCRDv{}_UniProt_Mapping.tsv'

def run(dba):
  uptdls = dba.get_uniprots_tdls()
  ct = len(uptdls)
  exp_ct = 0
  print(f"\nExporting UniProts/TDLs for {ct} TCRD targets")
  with open(OUTFILE, 'w') as ofh:
    ofh.write(f"UniProt_accession\tPharos_target\tTDL\n")
    for d in uptdls:
      ofh.write(f"{d['uniprot']}\t{d['uniprot']}\t{d['tdl']}\n")
      exp_ct += 1
      slmf.update_progress(exp_ct/ct)
  print(f"Wrote {exp_ct} lines to file {OUTFILE}")


if __name__ == '__main__':
  start_time = time.time()
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  dba = DBAdaptor({'dbhost': 'localhost', 'dbname': DBNAME})
  dbi = dba.get_dbinfo()
  print(f"Connected to TCRD database {DBNAME} (schema ver {dbi['schema_ver']}; data ver {dbi['data_ver']})")
  run(dba)
  # Add version number to filename and archive mapping file to old_versions dir
  mmver = '.'.join( dbi['data_ver'].split('.')[:2] )
  archivefn = ARCHIVE_FILEPAT.format(mmver)
  shutil.copy(OUTFILE, archivefn)
  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
