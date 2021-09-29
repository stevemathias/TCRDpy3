'''
Python3 functions for miscelaneous TCRD stuff.

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2021-04-09 10:25:14 smathias>
'''

def compute_tdl(tinfo):
  '''
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
