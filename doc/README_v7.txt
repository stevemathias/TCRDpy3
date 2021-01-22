Create empty schema with types
------------------------------
[smathias@juniper SQL]$ mysql
mysql> create database tcrd7;
mysql> use tcrd7
mysql> \. create-TCRDv7.sql


# UniProt
(venv) [smathias@juniper python]$ ./load-UniProt.py --dbname tcrd7 --loglevel 20

load-UniProt.py (v4.0.0) [Tue Jan 19 13:55:28 2021]:

Connected to TCRD database tcrd7 (schema ver 7.0.0; data ver 0.0.0)

Downloading https://raw.githubusercontent.com/evidenceontology/evidenceontology/master/eco.obo
         to ../data/EvidenceOntology/eco.obo

Downloading ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.xml.gz
         to uniprot_sprot_human.xml.gz
Uncompressing ../data/UniProt/uniprot_sprot_human.xml.gz

Downloading ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_rodents.xml.gz
         to uniprot_sprot_rodents.xml.gz
Uncompressing ../data/UniProt/uniprot_sprot_rodents.xml.gz

Parsing Evidence Ontology file ../data/EvidenceOntology/eco.obo

Parsing file ../data/UniProt/uniprot_sprot_human.xml
Loading data for 20394 UniProt records
Progress: [##################################################] 100.0% Done.
Processed 20394 UniProt records.
  Loaded 20394 targets/proteins

Parsing file ../data/UniProt/uniprot_sprot_rodents.xml
Loading data for 26887 UniProt records
Progress: [##################################################] 100.0% Done.
Processed 26887 UniProt records.
  Loaded 25170 Mouse and Rat nhproteins
  Skipped 1717 non-Mouse/Rat records

load-UniProt.py: Done. Elapsed time: 0:20:56.524

Some UniProt records have multiple Gene IDs. The loader takes the first
one, but this is not always the right one. So manual fixes to Gene IDs:
mysql> \. update_geneids_v7.sql

[smathias@juniper SQL]$ mysqldump tcrd7 > dumps7/tcrd7-1.sql


# HGNC
(venv) [smathias@juniper python]$ ./load-HGNC.py --dbname tcrd7 

load-HGNC.py (v4.0.0) [Wed Jan 20 14:03:34 2021]:

Connected to TCRD database tcrd7 (schema ver 7.0.0; data ver 0.0.0)

Processing 42415 lines in file ../data/HGNC/HGNC_20210120.tsv
Progress: [##################################################] 100.0% Done.
Processed 42415 lines - 20196 proteins annotated.
  Updated 20363 protein.chr values.
  Inserted 20363 HGNC ID xrefs
  Inserted 17136 MGI ID xrefs
WARNING: Found 217 discrepant HGNC symbols. See logfile ../log/tcrd7logs//load-HGNC.py.log for details
  Inserted 1275 new NCBI Gene IDs
WARNING: Found 193 discrepant NCBI Gene IDs. See logfile ../log/tcrd7logs//load-HGNC.py.log for details

load-HGNC.py: Done. Elapsed time: 0:07:51.533

[smathias@juniper SQL]$ mysqldump tcrd7 > dumps7/tcrd7-2.sql


