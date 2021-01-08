import os,sys,platform,time,re,gzip
from functools import reduce

def get_pw(f):
  f = open(f, 'r')
  pw = f.readline().strip()
  return pw

def conn_tcrd(init):
  if 'dbhost' in init:
    dbhost = init['dbhost']
  else:
    dbhost = DBHOST
  if 'dbport' in init:
    dbport = init['dbport']
  else:
    dbport = 3306
  if 'dbname' in init:
    dbname = init['dbname']
  else:
    dbname = DBNAME
  if 'dbuser' in init:
    dbuser = init['dbuser']
  else:
    dbuser = 'smathias'
  if 'pwfile' in init:
    dbauth = get_pw(init['pwfile'])
  else:
    dbauth = get_pw('/home/smathias/.dbirc')
  conn = mysql.connect(host=dbhost, port=dbport, db=dbname, user=dbuser, passwd=dbauth,
                       charset='utf8', init_command='SET NAMES UTF8')
  return conn

def secs2str(t):
  return "%d:%02d:%02d.%03d" % reduce(lambda ll,b : divmod(ll[0],b) + ll[1:], [(t*1000,),1000,60,60])

def wcl(fname):
  with open(fname) as f:
    for i, l in enumerate(f):
      pass
  return i + 1

def gzwcl(fname):
  with gzip.open(fname, 'rb') as f:
    for i, l in enumerate(f):
      pass
  return i + 1

def update_progress(progress):
  '''
  Displays/Updates a progress bar in a console.
  - The input should be a float between 0 and 1, although any int will be converted to a float.
  - An input value < 0 represents a 'halt'.
  - An value value >= 1 represents 100%
  '''
  barLength = 50 # Width of the progress bar
  status = ""
  if isinstance(progress, int):
    progress = float(progress)
  if not isinstance(progress, float):
    progress = 0
    status = "Error: input must be float.\r\n"
  if progress < 0:
    progress = 0
    status = "Aborted.\r\n"
  if progress >= 1:
    progress = 1
    status = "Done.\r\n"
  prog = int(round(barLength*progress))
  pbar = "\rProgress: [{0}] {1:.1f}% {2}".format("#"*prog + "-"*(barLength-prog), progress*100, status)
  sys.stdout.write(pbar)
  sys.stdout.flush()

def open_anything(fname, *args, **kwds):
  """Opens the given file. The file may be given as a file object
  or a filename. If the filename ends in ``.bz2`` or ``.gz``, it will
  automatically be decompressed on the fly. If the filename starts
  with ``http://``, ``https://`` or ``ftp://`` and there is no
  other argument given, the remote URL will be opened for reading.
  A single dash in place of the filename means the standard input.
  """
  #if isinstance(fname, file):
  if os.path.isfile(fname):
    infile = fname
  elif fname == "-":
    infile = sys.stdin
  elif (fname.startswith("http://") or fname.startswith("ftp://") or fname.startswith("https://")) and not kwds and not args:
    import urllib2
    infile = urllib2.urlopen(fname)
  elif fname[-4:] == ".bz2":
    import bz2
    infile = bz2.BZ2File(fname, *args, **kwds)
  elif fname[-3:] == ".gz":
    import gzip
    infile = gzip.GzipFile(fname, *args, **kwds)
  else:
    infile = open(fname, *args, **kwds)
  return infile

def tsv2csv(tsv):
  """
  Convert input lines of TSV to output lines of CSV.
  Returns CSV as a list.
  """
  csv = []
  for line in tsv.splitlines():
    fields = map( lambda f: '"'+f.replace('"','')+'"', re.split(r'\t', line) )
    csv.append(','.join(fields))
  return csv
