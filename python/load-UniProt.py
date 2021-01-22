#!/usr/bin/env python3
# Time-stamp: <2021-01-19 13:55:07 smathias>
"""Load protein data from UniProt.org into TCRD via the web.

Usage:
    load-UniProt.py [--debug | --quiet] [--dbhost=<str>] [--dbname=<str>] [--logfile=<file>] [--loglevel=<int>]
    load-UniProt.py -? | --help

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
__copyright__ = "Copyright 2014-2020, Steve Mathias"
__license__   = "Creative Commons Attribution-NonCommercial (CC BY-NC)"
__version__   = "4.0.0"

import os,sys,time,re
from docopt import docopt
from TCRD.DBAdaptor import DBAdaptor
import logging
from urllib.request import urlretrieve
import gzip
import obo
from lxml import etree, objectify
import slm_util_functions as slmf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

PROGRAM = os.path.basename(sys.argv[0])
TCRD_VER = '7' ## !!! CHECK THIS IS CORRECT !!! ##
LOGDIR = f"../log/tcrd{TCRD_VER}logs/"
LOGFILE = f"{LOGDIR}/{PROGRAM}.log"

UP_DOWNLOAD_DIR = '../data/UniProt/'
UP_BASE_URL = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/'
UP_HUMAN_FILE = 'uniprot_sprot_human.xml.gz'
UP_RODENT_FILE = 'uniprot_sprot_rodents.xml.gz' # uniprot_trembl_rodents.xml.gz
NS = '{http://uniprot.org/uniprot}'
ECO_BASE_URL = 'https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/'
ECO_DOWNLOAD_DIR = '../data/EvidenceOntology/'
ECO_OBO = 'eco.obo'

def download_eco(args):
  if os.path.exists(ECO_DOWNLOAD_DIR + ECO_OBO):
    os.remove(ECO_DOWNLOAD_DIR + ECO_OBO)
  if not args['--quiet']:
      print("\nDownloading {}".format(ECO_BASE_URL + ECO_OBO))
      print("         to {}".format(ECO_DOWNLOAD_DIR + ECO_OBO))
  urlretrieve(ECO_BASE_URL + ECO_OBO, ECO_DOWNLOAD_DIR + ECO_OBO)

def mk_eco_map(args):
  """
  Return a mapping of Evidence Ontology ECO IDs to Go Evidence Codes.
  """
  fn = ECO_DOWNLOAD_DIR + ECO_OBO
  if not args['--quiet']:
    print(f"\nParsing Evidence Ontology file {fn}")
  eco = {}
  eco_map = {}
  parser = obo.Parser(fn)
  for stanza in parser:
    eco[stanza.tags['id'][0].value] = stanza.tags
  regex = re.compile(r'GOECO:([A-Z]{2,3})')
  for e,d in eco.items():
    if not e.startswith('ECO:'):
      continue
    if 'xref' in d:
      for x in d['xref']:
        m = regex.match(x.value)
        if m:
          eco_map[e] = m.group(1)
  return eco_map

def download_uniprots(args):
  for gzfn in [UP_HUMAN_FILE, UP_RODENT_FILE]:
    gzfp = UP_DOWNLOAD_DIR + gzfn
    fp = gzfp.replace('.gz', '')
    if os.path.exists(gzfp):
      os.remove(gzfp)
    if os.path.exists(fp):
      os.remove(fp)
    if not args['--quiet']:
      print("\nDownloading {}".format(UP_BASE_URL + gzfn))
      print(f"         to {gzfn}")
    urlretrieve(UP_BASE_URL + gzfn, gzfp)
    if not args['--quiet']:
      print(f"Uncompressing {gzfp}")
    ifh = gzip.open(gzfp, 'rb')
    ofh = open(fp, 'wb')
    ofh.write( ifh.read() )
    ifh.close()
    ofh.close()
  
def load_human(args, dba, dataset_id, eco_map, logger, logfile):
  fn = UP_DOWNLOAD_DIR + UP_HUMAN_FILE.replace('.gz', '')
  if not args['--quiet']:
    print(f"\nParsing file {fn}")
  root = objectify.parse(fn).getroot()
  up_ct = len(root.entry)
  if not args['--quiet']:
    print(f"Loading data for {up_ct} UniProt records")
  logger.info(f"Loading data for {up_ct} UniProt records in file {fn}")
  ct = 0
  load_ct = 0
  xml_err_ct = 0
  dba_err_ct = 0
  for i in range(len(root.entry)):
    ct += 1
    slmf.update_progress(ct/up_ct)
    entry = root.entry[i]
    logger.info("Processing entry {}".format(entry.accession))
    tinit = entry2tinit(entry, dataset_id, eco_map)
    if not tinit:
      xml_err_ct += 1
      logger.error("XML Error for {}".format(entry.accession))
      continue
    tid = dba.ins_target(tinit)
    if not tid:
      dba_err_ct += 1
      continue
    logger.debug(f"Target insert id: {tid}")
    load_ct += 1
  print(f"Processed {ct} UniProt records.")
  print(f"  Loaded {load_ct} targets/proteins")
  if xml_err_ct > 0:
    print(f"WARNING: {xml_err_ct} XML parsing errors occurred. See logfile {logfile} for details.")
  if dba_err_ct > 0:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

def load_mouse_rat(args, dba, dataset_id, logger, logfile):
  fn = UP_DOWNLOAD_DIR + UP_RODENT_FILE.replace('.gz', '')
  if not args['--quiet']:
    print(f"\nParsing file {fn}")
  root = objectify.parse(fn).getroot()
  up_ct = len(root.entry)
  if not args['--quiet']:
    print(f"Loading data for {up_ct} UniProt records")
  logger.info(f"Loading data for {up_ct} UniProt records in file {fn}")
  ct = 0
  load_ct = 0
  skip_ct = 0
  xml_err_ct = 0
  dba_err_ct = 0
  for i in range(len(root.entry)):
    ct += 1
    slmf.update_progress(ct/up_ct)
    entry = root.entry[i]
    # filter for mouse and rat records
    for orgname in entry.organism.find(NS+'name'):
      if orgname.get('type') == 'scientific':
        break
    if orgname not in ['Mus musculus', 'Rattus norvegicus']:
      skip_ct += 1
      logger.debug("Skipping {} entry {}".format(orgname, entry.accession))
      continue
    logger.info("Processing entry {}".format(entry.accession))
    nhpinit = entry2nhpinit(entry, dataset_id)
    if not nhpinit:
      xml_err_ct += 1
      logger.error("XML Error for {}".format(entry.accession))
      continue
    nhpid = dba.ins_nhprotein(nhpinit)
    if not nhpid:
      dba_err_ct += 1
      continue
    logger.debug("Nhprotein insert id: {}".format(nhpid))
    load_ct += 1
  print(f"Processed {ct} UniProt records.")
  print(f"  Loaded {load_ct} Mouse and Rat nhproteins")
  if skip_ct > 0:
    print(f"  Skipped {skip_ct} non-Mouse/Rat records")
  if xml_err_ct > 0:
    print(f"WARNING: {xml_err_ct} XML parsing errors occurred. See logfile {logfile} for details.")
  if dba_err_ct > 0:
    print(f"WARNING: {dba_err_ct} DB errors occurred. See logfile {logfile} for details.")

def get_entry_by_accession(root, acc):
  """
  This is for debugging in IPython.
  """
  for i in range(len(root.entry)):
    entry = root.entry[i]
    if entry.accession == acc:
      return entry
  return None
                                              
def entry2tinit(entry, dataset_id, e2e):
  """
  Convert an entry element of type lxml.objectify.ObjectifiedElement parsed from a UniProt XML entry and return a dictionary suitable for passing to TCRD.DBAdaptor.ins_target().
  """
  target = {'name': entry.name.text, 'description': entry.protein.recommendedName.fullName.text,
            'ttype': 'Single Protein'}
  target['components'] = {}
  target['components']['protein'] = []
  protein = {'uniprot': entry.accession.text} # returns first accession, if there are multiple
  protein['name'] = entry.name.text
  protein['description'] = entry.protein.recommendedName.fullName.text
  protein['sym'] = None
  aliases = []
  if entry.find(NS+'gene'):
    if entry.gene.find(NS+'name'):
      for gn in entry.gene.name: # returns all gene.names
        if gn.get('type') == 'primary':
          protein['sym'] = gn.text
        elif gn.get('type') == 'synonym':
          # HGNC symbol alias
          aliases.append( {'type': 'symbol', 'dataset_id': dataset_id, 'value': gn.text} )
  protein['seq'] = str(entry.sequence).replace('\n', '')
  protein['up_version'] = entry.sequence.get('version')
  for acc in entry.accession: # returns all accessions
    if str(acc) != protein['uniprot']:
      aliases.append( {'type': 'uniprot', 'dataset_id': dataset_id, 'value': str(acc)} )
  if entry.protein.recommendedName.find(NS+'shortName') != None:
    sn = entry.protein.recommendedName.shortName.text
    aliases.append( {'type': 'uniprot', 'dataset_id': dataset_id, 'value': sn} )
  protein['aliases'] = aliases
  # TDL Infos, Family, Diseases, Pathways from comments
  tdl_infos = []
  pathways = []
  diseases = []
  if entry.find(NS+'comment'):
    for c in entry.comment:
      if c.get('type') == 'function':
        tdl_infos.append( {'itype': 'UniProt Function',  'string_value': str(c.getchildren()[0])} )
      if c.get('type') == 'pathway':
        pathways.append( {'pwtype': 'UniProt', 'name': str(c.getchildren()[0])} )
      if c.get('type') == 'similarity':
        protein['family'] = str(c.getchildren()[0])
      if c.get('type') == 'disease':
        if not c.find(NS+'disease'):
          continue
        if c.disease.find(NS+'name') == None:
          # some dont have a name, so skip those
          continue
        da = {'dtype': 'UniProt'}
        for el in c.disease.getchildren():
          if el.tag == NS+'name':
            da['name'] = el.text
          elif el.tag == NS+'description':
            da['description'] = el.text
          elif el.tag == NS+'dbReference':
            da['did'] = "{}:{}".format(str(el.attrib['type']), str(el.attrib['id']))
        if 'evidence' in c.attrib:
          da['evidence'] = str(c.attrib['evidence'])
        diseases.append(da)
  protein['tdl_infos'] = tdl_infos
  protein['diseases'] = diseases
  protein['pathways'] = pathways
  # GeneID, XRefs, GOAs from dbReferences
  xrefs = []
  goas = []
  for dbr in entry.dbReference:
    if dbr.attrib['type'] == 'GeneID':
      # Some UniProt records have multiple Gene IDs
      # So, only take the first one and fix manually after loading
      if 'geneid' not in protein:
        protein['geneid'] = str(dbr.attrib['id'])
    elif dbr.attrib['type'] in ['InterPro', 'Pfam', 'PROSITE', 'SMART']:
      xtra = None
      for el in dbr.findall(NS+'property'):
        if el.attrib['type'] == 'entry name':
          xtra = str(el.attrib['value'])
        xrefs.append( {'xtype': str(dbr.attrib['type']), 'dataset_id': dataset_id,
                       'value': str(dbr.attrib['id']), 'xtra': xtra} )
    elif dbr.attrib['type'] == 'GO':
      name = None
      goeco = None
      assigned_by = None
      for el in dbr.findall(NS+'property'):
        if el.attrib['type'] == 'term':
          name = str(el.attrib['value'])
        elif el.attrib['type'] == 'evidence':
          goeco = str(el.attrib['value'])
        elif el.attrib['type'] == 'project':
          assigned_by = str(el.attrib['value'])
      goas.append( {'go_id': str(dbr.attrib['id']), 'go_term': name,
                    'goeco': goeco, 'evidence': e2e[goeco], 'assigned_by': assigned_by} )
    elif dbr.attrib['type'] == 'Ensembl':
      xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id, 'value': str(dbr.attrib['id'])} )
      for el in dbr.findall(NS+'property'):
        if el.attrib['type'] == 'protein sequence ID':
          xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id,
                         'value': str(el.attrib['value'])} )
        elif el.attrib['type'] == 'gene ID':
          xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id,
                         'value': str(el.attrib['value'])} )
    elif dbr.attrib['type'] == 'STRING':
      xrefs.append( {'xtype': 'STRING', 'dataset_id': dataset_id, 'value': str(dbr.attrib['id'])} )
    elif dbr.attrib['type'] == 'DrugBank':
      xtra = None
      for el in dbr.findall(NS+'property'):
        if el.attrib['type'] == 'generic name':
          xtra = str(el.attrib['value'])
      xrefs.append( {'xtype': 'DrugBank', 'dataset_id': dataset_id, 'value': str(dbr.attrib['id']),
                     'xtra': xtra} )
    elif dbr.attrib['type'] in ['BRENDA', 'ChEMBL', 'MIM', 'PANTHER', 'PDB', 'RefSeq', 'UniGene']:
        xrefs.append( {'xtype': str(dbr.attrib['type']), 'dataset_id': dataset_id,
                       'value': str(dbr.attrib['id'])} )
  protein['goas'] = goas
  # Keywords
  for kw in entry.keyword:
    xrefs.append( {'xtype': 'UniProt Keyword', 'dataset_id': dataset_id,
                   'value': str(kw.attrib['id']), 'xtra': str(kw)} )
  protein['xrefs'] = xrefs
  # Expression
  exps = []
  for ref in entry.reference:
    if ref.find(NS+'source'):
      if ref.source.find(NS+'tissue'):
        ex = {'etype': 'UniProt Tissue', 'tissue': ref.source.tissue.text, 'boolean_value': 1}
        for el in ref.citation.findall(NS+'dbReference'):
          if el.attrib['type'] == 'PubMed':
            ex['pubmed_id'] = str(el.attrib['id'])
        exps.append(ex)
  protein['expressions'] = exps
  # Features
  features = []
  for f in entry.feature:
    init = {'type': str(f.attrib['type'])}
    if 'evidence' in f.attrib:
      init['evidence'] = str(f.attrib['evidence'])
    if 'description' in f.attrib:
      init['description'] = str(f.attrib['description'])
    if 'id' in f.attrib:
      init['srcid'] = str(f.attrib['id'])
    for el in f.location.getchildren():
      if el.tag == NS+'position':
        init['position'] = str(el.attrib['position'])
      else:
        if el.tag == NS+'begin':
          if 'position' in el.attrib:
            init['begin'] = str(el.attrib['position'])
        if el.tag == NS+'end':
          if 'position' in el.attrib:
            init['end'] = str(el.attrib['position'])
    features.append(init)
  protein['features'] = features
  target['components']['protein'].append(protein)
  return target

def entry2nhpinit(entry, dataset_id):
  """
  Convert an entry element of type lxml.objectify.ObjectifiedElement parsed from a UniProt XML entry and return a dictionary suitable for passing to TCRD.DBAdaptor.ins_nhprotein().
  """
  nhprotein = {'uniprot': entry.accession.text, 'name': entry.name.text,
               'taxid': str(entry.organism.dbReference.attrib['id'])}
  # description
  if entry.protein.find(NS+'recommendedName'):
    nhprotein['description'] = entry.protein.recommendedName.fullName.text
  elif entry.protein.find(NS+'submittedName'):
    nhprotein['description'] = entry.protein.submittedName.fullName.text
  # sym
  if entry.find(NS+'gene'):
    if entry.gene.find(NS+'name'):
       if entry.gene.name.get('type') == 'primary':
         nhprotein['sym'] = entry.gene.name.text
  # species
  for name in entry.organism.name:
    if name.attrib["type"] == "scientific":
      nhprotein['species'] = name.text
  # geneid
  for dbr in entry.dbReference:
    if dbr.attrib['type'] == 'GeneID':
      nhprotein['geneid'] = str(dbr.attrib['id'])
  xrefs = []
  for dbr in entry.dbReference:
    if(dbr.attrib["type"] == "Ensembl"):
      xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id, 'value': str(dbr.attrib['id'])} )
      for el in dbr.findall(NS+'property'):
        if el.attrib['type'] == 'protein sequence ID':
          xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id,
                         'value': str(el.attrib['value'])} )
        elif el.attrib['type'] == 'gene ID':
          xrefs.append( {'xtype': 'Ensembl', 'dataset_id': dataset_id,
                         'value': str(el.attrib['value'])} )
    elif dbr.attrib['type'] == 'STRING':
      xrefs.append( {'xtype': 'STRING', 'dataset_id': dataset_id, 'value': str(dbr.attrib['id'])} )
  nhprotein['xrefs'] = xrefs
  return nhprotein
  

if __name__ == '__main__':
  print("\n{} (v{}) [{}]:\n".format(PROGRAM, __version__, time.strftime("%c")))
  start_time = time.time()

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

  download_eco(args)
  download_uniprots(args)

  # UniProt uses ECO IDs in GOAs, not GO evidence codes, so get a mapping of
  # ECO IDs to GO evidence codes
  eco_map = mk_eco_map(args)
  
  # Human proteins
  # Dataset and Provenance
  # This has to be done first because the dataset id is needed for xrefs and aliases
  dataset_id = dba.ins_dataset( {'name': 'UniProt', 'source': f"UniProt XML file {UP_HUMAN_FILE} from {UP_BASE_URL}", 'app': PROGRAM, 'app_version': __version__, 'url': 'https://www.uniprot.org'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  provs = [ {'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'name'},
            {'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'description'},
            {'dataset_id': dataset_id, 'table_name': 'target', 'column_name': 'ttype'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'name'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'description'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'uniprot'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'up_version'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'sym'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'seq'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'geneid'},
            {'dataset_id': dataset_id, 'table_name': 'protein', 'column_name': 'family'},
            {'dataset_id': dataset_id, 'table_name': 'tdl_info', 'where_clause': "itype = 'UniProt Function'"},
            {'dataset_id': dataset_id, 'table_name': 'goa'},  
            {'dataset_id': dataset_id, 'table_name': 'expression', 'where_clause': "etype = 'UniProt Tissue'"},
            {'dataset_id': dataset_id, 'table_name': 'pathway', 'where_clause': "pwtype = 'UniProt'"},
            {'dataset_id': dataset_id, 'table_name': 'disease', 'where_clause': "dtype = 'UniProt'"},
            {'dataset_id': dataset_id, 'table_name': 'feature'},
            {'dataset_id': dataset_id, 'table_name': 'xref', 'where_clause': f"dataset_id = {dataset_id}"},
            {'dataset_id': dataset_id, 'table_name': 'alias', 'where_clause': f"dataset_id = {dataset_id}"} ]
  for prov in provs:
    rv = dba.ins_provenance(prov)
    assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  load_human(args, dba, dataset_id, eco_map, logger, logfile)
  
  # Mouse and Rat proteins
  # Dataset and Provenance
  # As for human, we need the dataset id for xrefs and aliases
  dataset_id = dba.ins_dataset( {'name': 'UniProt Mouse and Rat Proteins', 'source': f"Mouse and Rat  from UniProt XML file {UP_RODENT_FILE} from {UP_BASE_URL}", 'app': PROGRAM, 'app_version': __version__, 'url': 'https://www.uniprot.org'} )
  assert dataset_id, f"Error inserting dataset See logfile {logfile} for details."
  rv = dba.ins_provenance({'dataset_id': dataset_id, 'table_name': 'nhprotein'})
  assert rv, f"Error inserting provenance. See logfile {logfile} for details."
  load_mouse_rat(args, dba, dataset_id, logger, logfile)

  elapsed = time.time() - start_time
  print("\n{}: Done. Elapsed time: {}\n".format(PROGRAM, slmf.secs2str(elapsed)))
