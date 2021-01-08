'''
Generate Target Importance and Novelty Explorer (TIN-X) files.

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2020-12-11 10:28:58 smathias>
'''

from functools import cmp_to_key
import logging

def cmp_pmids_scores(a, b):
  '''
  This is the sorting function for PubMed Rankings. See the TINX method 
  compute_pubmed_rankings() for more.
  a and b are tuples: (PMID, score)
  This sorts first by score ascending and then by PMID descending.
  '''
  if a[1] > b[1]:
    return 1
  elif a[1] < b[1]:
    return -1
  elif a[0] > b[0]:
    return -1
  elif a[1] < b[0]:
    return 1
  else:
    return 0

class TINX():
  _LogFile = '/tmp/TINX.log'
  _LogLevel = logging.INFO
  
  def __init__(self, cfg, dba, do):
    # input JensenLab mentions files:
    self._protein_file = cfg['TINX_PROTEIN_FILE']
    self._disease_file = cfg['TINX_DISEASE_FILE']

    # directory to store output files:
    self._outdir = cfg['OUTDIR']
    
    # our TCRD.DBAdaptor:
    self._dba = dba

    # our parsed DO names and defs
    self._do = do
    
    # our logger:
    if 'logfile' in cfg:
      lfn = cfg['logfile']
    else:
      lfn = self._LogFile
    if 'loglevel' in cfg:
      ll = cfg['loglevel']
    else:
      ll = self._LogLevel
      self._logger = logging.getLogger(__name__)
      self._logger.propagate = False # turns off console logging
      fh = logging.FileHandler(lfn)
      self._logger.setLevel(ll)
      fmtr = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
      fh.setFormatter(fmtr)
      self._logger.addHandler(fh)

    # The results of parsing the JensenLab mentions files will be stored in the
    # following dictionaries:
    self._pid2pmids = {}  # 'TCRD.protein.id,UniProt' => set of all PMIDs that mention the protein
                          # Including the UniProt accession in the key is just for convenience when
                          # checking the output. It is not used for anything.
    self._doid2pmids = {} # DOID => set of all PMIDs that mention the disease
    self._pmid_disease_ct = {} # PMID => count of diseases mentioned in a given paper 
    self._pmid_protein_ct = {} # PMID => count of proteins mentioned in a given paper

  def parse_protein_mentions(self):
    line_ct = slmf.wcl( self._protein_file )
    self._logger.info("\nProcessing {} lines in protein file {}".format(line_ct, self._protein_file))
    with open(self._protein_file, 'rU') as tsvf:
      ct = 0
      skip_ct = 0
      notfnd = set()
      for line in tsvf:
        ct += 1
        if not line.startswith('ENSP'):
          skip_ct += 1
          continue
        data = line.rstrip().split('\t')
        ensp = data[0]
        pmids = set([int(pmid) for pmid in data[1].split()])
        pids = self._dba.find_protein_ids({'stringid': ensp})
        if not pids:
          # if we don't find a protein by stringid, which is the more reliable and
          # prefered way, try by Ensembl xref
          pids = dba.find_protein_ids_by_xref({'xtype': 'Ensembl', 'value': ensp})
          if not pids:
            notfnd.add(ensp)
            continue
        for pid in pids:
          k = "{},{}".format(p['id'], p['uniprot'])
          if k in self._pid2pmids:
            self._pid2pmids[k] = self._pid2pmids[k].union(pmids)
          else:
            self._pid2pmids[k] = set(pmids)
          for pmid in pmids:
            if pmid in self._pmid_protein_ct:
              self._pmid_protein_ct[pmid] += 1.0
            else:
              self._pmid_protein_ct[pmid] = 1.0
    for ensp in notfnd:
      self._logger.warn(f"No protein found for {ensp}")
    self._logger.info(f"\n{ct} lines processed")
    self._logger.info(f"  Skipped {skip_ct} non-ENSP lines")
    self._logger.info("  Saved {} protein to PMIDs mappings".format(len(self._pid2pmids)))
    self._logger.info("  Saved {} PMID to protein count mappings".format(len(self._pmid_protein_ct)))
    if notfnd:
      self._logger.info("  No target found for {} ENSPs.".format(len(notfnd)))
    return (len(self._pid2pmids), len(self._pmid_protein_ct))

  def parse_disease_mentions(self):
    line_ct = slmf.wcl( self._disease_file )
    self._logger.info("\nProcessing {} lines in disease file {}".format(line_ct, self._disease_file))
    with open(self._disease_file, 'rU') as tsvf:
      ct = 0
      skip_ct = 0
      notfnd = set()
      for line in tsvf:
        ct += 1
        if not line.startswith('DOID:'):
          skip_ct += 1
          continue
        data = line.rstrip().split('\t')
        doid = data[0]
        pmids = set([int(pmid) for pmid in data[1].split()])
        if doid not in self._do:
          self._logger.warn(f"{doid} not found in DO")
          notfnd.add(doid)
          continue
        if doid in self._doid2pmids:
          self._doid2pmids[doid] = self._doid2pmids[doid].union(pmids)
        else:
          self._doid2pmids[doid] = set(pmids)
        for pmid in pmids:
          if pmid in self._pmid_disease_ct:
            self._pmid_disease_ct[pmid] += 1.0
          else:
            self._pmid_disease_ct[pmid] = 1.0
    for doid in notfnd:
      self._logger.warn(f"No DO entry found for {doid}")
    self._logger.info(f"\n{ct} lines processed.")
    self._logger.info(f"  Skipped {skip_ct} non-DOID lines")
    self._logger.info("  Saved {} DOID to PMIDs mappings".format(len(self._doid2pmids)))
    self._logger.info("  Saved {} PMID to disease count mappings".format(len(self._pmid_disease_ct)))
    if notfnd:
      self._logger.info("WARNNING: No entry found in DO map for {} DOIDs.".format(len(notfnd)))
    return (len(self._doid2pmids), len(self._pmid_disease_ct))
  
  def compute_protein_novelty(self):
    '''
    To calculate protein novelty scores, each paper (PMID) is assigned a
    fractional target (FT) score of one divided by the number of proteins
    mentioned in it. The novelty score of a given protein is one divided
    by the sum of the FT scores for all the papers mentioning that protein.
    '''
    self._logger.info("\nComputing protein novely scores")
    ct = 0
    ofn = self._outdir + 'ProteinNovelty.csv'
    with open(ofn, 'w') as pnovf:
      pnovf.write("Protein ID,UniProt,Novelty\n")
      for pidup,pmids in self._pid2pmids.items():
        ct += 1
        ft_score_sum = 0.0
        for pmid in pmids:
          ft_score_sum += 1.0 / self._pmid_protein_ct[pmid]
        novelty = 1.0 / ft_score_sum
        pnovf.write( "%s,%.8f\n" % (pidup, novelty) )
    self._logger.info(f"  Wrote {ct} protein novelty scores to file {ofn}")
    return (ct, ofn)

  def compute_disease_novelty(self):
    '''
    To calculate disease novelty scores, each paper (PMID) is assigned a
    fractional disease (FD) score of one divided by the number of diseases
    mentioned in it. The novelty score of a given disease is one divided
    by the sum of the FD scores for all the papers mentioning that protein.
    '''
    self._logger.info("\nComputing disease novely scores")
    ct = 0
    ofn = self._outdir + 'DiseaseNovelty.csv'
    with open(ofn, 'w') as dnovf:
      dnovf.write("DOID,Novelty\n")
      for doid,pmids in self._doid2pmids.items():
        ct += 1
        fd_score_sum = 0.0
        for pmid in pmids:
          ft_score_sum += 1.0 / self._pmid_disease_ct[pmid]
        novelty = 1.0 / ft_score_sum
        dnovf.write( "%s,%.8f\n" % (doid, novelty) )
    self._logger.info(f"  Wrote {ct} disease novelty scores to file {ofn}")
    return (ct, ofn)

  def compute_importances(self):
    '''
    To calculate importance scores, each paper is assigned a fractional
    disease-target (FDT) score of one divided by the product of the
    number of targets mentioned and the number of diseases
    mentioned. The importance score for a given disease-target pair is
    the sum of the FDT scores for all papers mentioning that disease and
    protein.
    '''
    self._logger.info("\nComputing importance scores")
    ct = 0
    ofn = self._outdir + 'Importance.csv'
    with open(ofn, 'w') as impf:
      impf.write("DOID,Protein ID,UniProt,Score\n")
      for pidup,ppmids in self._pid2pmids.items():
        for doid,dpmids in self._doid2pmids.items():
          pd_pmids = ppmids.intersection(dpmids)
          fdt_score_sum = 0.0
          for pmid in pd_pmids:
            fdt_score_sum += 1.0 / ( self._pmid_protein_ct[pmid] * self._pmid_disease_ct[pmid] )
          if fdt_score_sum > 0:
            ct += 1
            impf.write( "%s,%s,%.8f\n" % (doid, pidup, fdt_score_sum) )
    print(f"  Wrote {ct} importance scores to file {ofn}")
    return (ct, ofn)

  def compute_pubmed_rankings(self):
    '''
    PMIDs are ranked for a given disease-target pair based on a score
    calculated by multiplying the number of targets mentioned and the
    number of diseases mentioned in that paper. Lower scores have a lower
    rank (higher priority). If the scores do not discriminate, PMIDs are
    reverse sorted by value with the assumption that larger PMIDs are
    newer and of higher priority.
    '''
    self._logger.info("\nComputing PubMed rankings")
    ct = 0
    ofn = self._outdir + 'PMIDRanking.csv'
    with open(ofn, 'w') as pmrf:
      pmrf.write("DOID,Protein ID,UniProt,PubMed ID,Rank\n")
      for pidup,ppmids in self._pid2pmids.items():
        for doid,dpmids in self._doid2pmids.items():
          pd_pmids = ppmids.intersection(dpmids)
          scores = [] # scores are tuples of (PMID, protein_mentions*disease_mentions)
          for pmid in pd_pmids:
            scores.append( (pmid, self._pmid_protein_ct[pmid] * self._pmid_disease_ct[pmid]) )
          if len(scores) > 0:
            scores.sort(key = cmp_to_key(cmp_pmids_scores))
            for i,t in enumerate(scores):
              ct += 1
              pmrf.write( "%s,%s,%d,%d\n" % (doid, pidup, t[0], i) )
    self._logger.info(f"  Wrote {ct} PubMed rankings to file {ofn}")
    return (ct, ofn)
    


