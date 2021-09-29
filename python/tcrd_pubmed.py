'''
Python3 functions for TCRD PubMed stuff.

Steve Mathias
smathias@salud.unm.edu
Time-stamp: <2021-04-09 10:23:38 smathias>
'''
import requests
import urllib.parse
import re
import time
from bs4 import BeautifulSoup
import calendar
import slm_util_functions as slmf

# E-Utils 
EMAIL = 'smathias@salud.unm.edu'
TOOL = 'tcrd_pubmed.py'
EUTILS_API_KEY = slmf.get_pw('/home/smathias/.eutils_api_key')
EFETCH_BASE_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# map abbreviated month names to ints
MONTHS_RDICT = {v: str(i) for i,v in enumerate(calendar.month_abbr)}
MLD_REGEX = re.compile(r'(\d{4}) (\w{3}) (\d\d?)-')

def fetch_pubmeds(pmids):
  """
  Use EUtils to bulk fetch XML PubMed records and return a corresponding list of 'PubmedArticle' bs4.elements.
  """
  #url = "{}?&db=pubmed&retmode=xml&email={}&tool={}&id={}".format(EFETCH_BASE_URL, urllib.parse.quote(EMAIL), urllib.parse.quote(TOOL), ','.join(pmids))
  url = EFETCH_BASE_URL + "?db=pubmed&retmode=xml&api_key={}&id={}".format(EUTILS_API_KEY, ','.join(pmids))
  attempt = 1
  r = None
  while attempt <= 5:
    try:
      r = requests.get(url)
      break
    except:
      attempt += 1
      time.sleep(1)
  if not r or r.status_code != 200:
    return False
  soup = BeautifulSoup(r.text, "xml")
  pmas = soup.find('PubmedArticleSet')
  return [pma for pma in pmas.findAll('PubmedArticle')]

def pubdate2isostr(pubdate):
  """
  Turn a PubDate XML element into an ISO-type string (ie. YYYY-MM-DD).
  """
  if pubdate.find('MedlineDate'):
    mld = pubdate.find('MedlineDate').text
    m = MLD_REGEX.search(mld)
    if not m:
      return None
    month = MONTHS_RDICT.get(m.groups(1), None)
    if not month:
      return m.groups()[0]
    return "{}-{}-{}".format(m.groups()[0], month, m.groups()[2])
  else:
    year = pubdate.find('Year').text
    if not pubdate.find('Month'):
      return year
    month = pubdate.find('Month').text
    if not month.isdigit():
      month = MONTHS_RDICT.get(month, None)
      if not month:
        return year
    if pubdate.find('Day'):
      day = pubdate.find('Day').text
      return "{}-{}-{}".format(year, month.zfill(2), day.zfill(2))
    else:
      return "{}-{}".format(year, month.zfill(2))

def parse_pubmed_article(pma):
  """
  Parse a 'PubmedArticle' bs4.element and return a tuple for TCRD's pubmed table.
  """
  pmid = pma.find('PMID').text
  bs_article = pma.find('Article')
  tlist = bs_article.find('ArticleTitle').text.split()
  title = ' '.join(tlist) # split/join is to remove tabs/newlines/multi-spaces
  bs_journal = bs_article.find('Journal')
  journal = date = authors = abstract = ''
  if bs_journal.find('Title'):
    journal = bs_journal.find('Title').text
  if bs_journal.find('PubDate'):
    date = pubdate2isostr(bs_journal.find('PubDate'))
  bs_authors = pma.findAll('Author')
  if len(bs_authors) > 0:
    if len(bs_authors) > 5:
      # For papers with more than five authors, the authors field will be
      # formated as: "Mathias SL and 42 more authors."
      a = bs_authors[0]
      # if the first author has no last name, we skip populating the authors field
      if a.find('LastName'):
        astr = "{}".format(a.find('LastName').text)
        if a.find('ForeName'):
          astr += ", {}".format(a.find('ForeName').text)
        elif a.find('Initials'):
          astr += " {}".format(a.find('Initials').text)
        authors = "{} and {} more authors.".format(astr, len(bs_authors)-1)
    else:
      # For papers with five or fewer authors, the authors field will have all their names
      auth_strings = []
      last_auth = bs_authors.pop()
      # if the last author has no last name, we skip populating the authors field
      if last_auth.find('LastName'):
        last_auth_str = last_auth.find('LastName').text
        if last_auth.find('ForeName'):
          last_auth_str += ", {}".format(last_auth.find('ForeName').text)
        elif last_auth.find('Initials'):
          last_auth_str += " {}".format(last_auth.find('Initials').text)
        for a in bs_authors:
          if a.find('LastName'): # if authors have no last name, we skip them
            astr = a.find('LastName').text
            if a.find('ForeName'):
              astr += ", {}".format(a.find('ForeName').text)
            elif a.find('Initials'):
              astr += " {}".format(a.find('Initials').text)
            auth_strings.append(astr)
        authors = "{} and {}.".format("; ".join(auth_strings), last_auth_str)
  if bs_article.find('AbstractText'):
    alist = bs_article.find('AbstractText').text.split()
    abstract = ' '.join(alist) # split/join is to remove tabs/newlines/multi-spaces
  return pmid, title, journal, date, authors, abstract

