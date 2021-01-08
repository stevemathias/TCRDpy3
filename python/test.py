#!/usr/bin/env python3
# Time-stamp: <2020-12-01 17:43:38 smathias>
__author__    = "Steve Mathias"
__email__     = "smathias @salud.unm.edu"
__org__       = "Translational Informatics Division, UNM School of Medicine"
__copyright__ = "Copyright 2020, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "1.0.0"

import os,sys,time
from TCRD.DBAdaptor import DBAdaptor

PROGRAM = os.path.basename(sys.argv[0])
DBNAME = 'tcrd6'

if __name__ == '__main__':
  print("\n{} v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))

  dba = DBAdaptor({'dbname': DBNAME})
  dbi = dba.get_dbinfo()
  print("Connected to TCRD database {} (schema ver {}; data ver {})\n".format(dbi['dbname'], dbi['schema_ver'], dbi['data_ver']))
