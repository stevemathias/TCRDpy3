'''
Python3 API for IDG-KMC Target Central Repository Database versions >= 6.*.*

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2021-02-25 08:07:53 smathias>
'''
import sys
import platform
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from contextlib import closing
from collections import defaultdict
import logging
from TCRD.Create import CreateMethodsMixin
from TCRD.Read import ReadMethodsMixin
from TCRD.Update import UpdateMethodsMixin
from TCRD.Delete import DeleteMethodsMixin
  
class DBAdaptor(CreateMethodsMixin, ReadMethodsMixin, UpdateMethodsMixin, DeleteMethodsMixin):
  # Default config
  _DBHost = 'localhost' ;
  _DBPort = 3306 ;
  _DBName = 'tcrd' ;
  _DBUser = 'smathias'
  if platform.system() == 'Darwin':
    _PWFile = '/Users/smathias/.dbirc'
  else:
    _PWFile = '/home/smathias/.dbirc'
  _LogFile = '/tmp/TCRDpy3_DBA.log'
  _LogLevel = logging.WARNING

  def __init__(self, init):
    # DB Connection
    if 'dbhost' in init:
      dbhost = init['dbhost']
    else:
      dbhost = self._DBHost
    if 'dbport' in init:
      dbport = init['dbport']
    else:
      dbport = self._DBPort
    if 'dbname' in init:
      dbname = init['dbname']
    else:
      dbname = self._DBName
    if 'dbuser' in init:
      dbuser = init['dbuser']
    else:
      dbuser = self._DBUser
    if 'pwfile' in init:
      dbauth = self._get_auth(init['pwfile'])
    else:
      dbauth = self._get_auth(self._PWFile)
    # Logging
    # levels are:
    # CRITICAL 50
    # ERROR    40
    # WARNING  30
    # INFO     20
    # DEBUG    10
    # NOTSET	0
    if 'logger_name' in init:
      # use logger from calling module
      ln = init['logger_name'] + '.auxiliary.DBAdaptor'
      self._logger = logging.getLogger(ln)
    else:
      if 'logfile' in init:
        lfn = init['logfile']
      else:
        lfn = self._LogFile
      if 'loglevel' in init:
        ll = init['loglevel']
      else:
        ll = self._LogLevel
      self._logger = logging.getLogger(__name__)
      self._logger.propagate = False # turns off console logging
      fh = logging.FileHandler(lfn)
      self._logger.setLevel(ll)
      fmtr = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
      fh.setFormatter(fmtr)
      self._logger.addHandler(fh)

    self._logger.debug('Instantiating new TCRD DBAdaptor')
    self._connect(host=dbhost, port=dbport, db=dbname, user=dbuser, passwd=dbauth)
      
    self._cache_info_types()
    self._cache_xref_types()
    self._cache_expression_types()
    self._cache_phenotype_types()
    #self._cache_gene_attribute_types()

  def __del__(self):
    self._conn.close()
    self._logger.debug('connection closed')

  def get_dbinfo(self):
    self._logger.debug('get_dbinfo() entry')
    sql = 'SELECT * FROM dbinfo'
    self._logger.debug('creating cursor')
    try:
      cur = self._conn.cursor(dictionary=True)
    except Error as e:
      self._logger.error(f"Error creating cursor: {e}")
    self._logger.debug(f"executing query: '{sql}'")
    try:
      cur.execute(sql)
    except Error as e:
      self._logger.error(f"Error executing query: {e}")
    self._logger.debug("fetching data")
    try:
      row = cur.fetchone()
    except Error as e:
      self._logger.error(f"Error fetching data: {e}")
    cur.close()
    return row

  def warning(*objs):
    print("TCRD DBAdaptor WARNING: ", *objs, file=sys.stderr)

  def error(*objs):
    print("TCRD DBAdaptor ERROR: ", *objs, file=sys.stderr)

  #
  # Private Methods
  #
  def _connect(self, host, port, db, user, passwd):
    '''
    Function  : Connect to a TCRD database
    Arguments : N/A
    Returns   : N/A
    Scope     : Private
    Comments  : Database connection object is stored as private instance varibale
    '''
    try:
      self._conn = mysql.connector.connect(host=host, port=port, db=db, user=user,
                                         passwd=passwd, charset='utf8')
    except Error as e:
      if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        self._logger.error("Error connecting to MySQL: Bad user name or password")
      elif e.errno == errorcode.ER_BAD_DB_ERROR:
        self._logger.error("Error connecting to MySQL: Database does not exist")
      else:
        self._logger.error(f"Error connecting to MySQL: {e}")
    self._logger.debug(f"Successful connection to database {db}: {self._conn}")

  def _get_auth(self, pw_file):
    '''
    Function  : Get database password from a file.
    Arguments : Path to file
    Returns   : Database password
    Scope     : Private
    Comments  :
    '''
    f = open(pw_file, 'r')
    pw = f.readline().strip()
    return pw

  def _cache_info_types(self):
    if hasattr(self, '_info_types'):
        return
    else:
      with closing(self._conn.cursor()) as curs:
        curs.execute("SELECT name, data_type FROM info_type")
        self._info_types = {}
        for it in curs:
          k = it[0]
          t = it[1]
          if t == 'String':
            v = 'string_value'
          elif t == 'Integer':
            v = 'integer_value'
          elif t == 'Number':
            v = 'number_value'
          elif t == 'Boolean':
            v = 'boolean_value'
          elif t == 'Date':
            v = 'date_value'
          self._info_types[k] = v

  def _cache_xref_types(self):
    if hasattr(self, '_xref_types'):
        return
    else:
      with closing(self._conn.cursor()) as curs:
        curs.execute("SELECT name FROM xref_type")
        self._xref_types = []
        for xt in curs:
          self._xref_types.append(xt[0])

  def _cache_expression_types(self):
    if hasattr(self, '_expression_types'):
        return
    else:
      with closing(self._conn.cursor()) as curs:
        curs.execute("SELECT name, data_type FROM expression_type")
        self._expression_types = {}
        for ex in curs:
          k = ex[0]
          t = ex[1]
          if t == 'String':
            v = 'string_value'
          elif t == 'Number':
            v = 'number_value'
          elif t == 'Boolean':
            v = 'boolean_value'
          self._expression_types[k] = v

  def _cache_phenotype_types(self):
    if hasattr(self, '_gene_phenotype_types'):
        return
    else:
      with closing(self._conn.cursor()) as curs:
        curs.execute("SELECT name FROM phenotype_type")
        self._phenotype_types = []
        for row in curs:
          self._phenotype_types.append(row[0])

  def _cache_gene_attribute_types(self):
    if hasattr(self, '_gene_attribute_types'):
        return
    else:
      with closing(self._conn.cursor()) as curs:
        curs.execute("SELECT id, name FROM gene_attribute_type")
        self._gene_attribute_types = {}
        for row in curs:
          self._gene_attribute_types[row[1]] = row[0]


if __name__ == '__main__':
  dba = DBAdaptor({'dbname': 'tcrd6', 'loglevel': 10, 'logfile': './TCRD-DBA.log'})
  dbi = dba.get_dbinfo()
  print("DBInfo: {}\n".format(dbi))


