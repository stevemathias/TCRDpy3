-- MySQL dump 10.13  Distrib 5.6.24, for Linux (x86_64)
--
-- Host: localhost    Database: tcrd7
-- ------------------------------------------------------
-- Server version	5.6.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alias`
--

DROP TABLE IF EXISTS `alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `type` enum('symbol','uniprot') COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `dataset_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `alias_idx1` (`protein_id`),
  KEY `alias_idx2` (`dataset_id`),
  CONSTRAINT `fk_alias_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`),
  CONSTRAINT `fk_alias_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alias`
--

LOCK TABLES `alias` WRITE;
/*!40000 ALTER TABLE `alias` DISABLE KEYS */;
/*!40000 ALTER TABLE `alias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinvar`
--

DROP TABLE IF EXISTS `clinvar`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinvar` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `clinvar_phenotype_id` int(11) NOT NULL,
  `alleleid` int(11) NOT NULL,
  `type` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `review_status` varchar(60) COLLATE utf8_unicode_ci NOT NULL,
  `clinical_significance` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `clin_sig_simple` int(11) DEFAULT NULL,
  `last_evaluated` date DEFAULT NULL,
  `dbsnp_rs` int(11) DEFAULT NULL,
  `dbvarid` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `origin` varchar(60) COLLATE utf8_unicode_ci DEFAULT NULL,
  `origin_simple` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `assembly` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  `chr` varchar(2) COLLATE utf8_unicode_ci DEFAULT NULL,
  `chr_acc` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `start` int(11) DEFAULT NULL,
  `stop` int(11) DEFAULT NULL,
  `number_submitters` int(2) DEFAULT NULL,
  `tested_in_gtr` tinyint(1) DEFAULT NULL,
  `submitter_categories` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `clinvar_idx1` (`protein_id`),
  KEY `clinvar_idx2` (`clinvar_phenotype_id`),
  CONSTRAINT `fk_clinvar__clinvar_phenotype` FOREIGN KEY (`clinvar_phenotype_id`) REFERENCES `clinvar_phenotype` (`id`),
  CONSTRAINT `fk_clinvar_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinvar`
--

LOCK TABLES `clinvar` WRITE;
/*!40000 ALTER TABLE `clinvar` DISABLE KEYS */;
/*!40000 ALTER TABLE `clinvar` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinvar_phenotype`
--

DROP TABLE IF EXISTS `clinvar_phenotype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinvar_phenotype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinvar_phenotype`
--

LOCK TABLES `clinvar_phenotype` WRITE;
/*!40000 ALTER TABLE `clinvar_phenotype` DISABLE KEYS */;
/*!40000 ALTER TABLE `clinvar_phenotype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clinvar_phenotype_xref`
--

DROP TABLE IF EXISTS `clinvar_phenotype_xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clinvar_phenotype_xref` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `clinvar_phenotype_id` int(11) NOT NULL,
  `source` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `clinvar_phenotype_idx1` (`clinvar_phenotype_id`),
  CONSTRAINT `fk_clinvar_phenotype_xref__clinvar_phenotype` FOREIGN KEY (`clinvar_phenotype_id`) REFERENCES `clinvar_phenotype` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clinvar_phenotype_xref`
--

LOCK TABLES `clinvar_phenotype_xref` WRITE;
/*!40000 ALTER TABLE `clinvar_phenotype_xref` DISABLE KEYS */;
/*!40000 ALTER TABLE `clinvar_phenotype_xref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cmpd_activity`
--

DROP TABLE IF EXISTS `cmpd_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cmpd_activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `catype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `cmpd_id_in_src` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `cmpd_name_in_src` text COLLATE utf8_unicode_ci,
  `smiles` text COLLATE utf8_unicode_ci,
  `act_value` decimal(10,8) DEFAULT NULL,
  `act_type` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reference` text COLLATE utf8_unicode_ci,
  `pubmed_ids` text COLLATE utf8_unicode_ci,
  `cmpd_pubchem_cid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cmpd_activity_idx1` (`catype`),
  KEY `cmpd_activity_idx2` (`target_id`),
  CONSTRAINT `fk_chembl_activity__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cmpd_activity__cmpd_activity_type` FOREIGN KEY (`catype`) REFERENCES `cmpd_activity_type` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cmpd_activity`
--

LOCK TABLES `cmpd_activity` WRITE;
/*!40000 ALTER TABLE `cmpd_activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `cmpd_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cmpd_activity_type`
--

DROP TABLE IF EXISTS `cmpd_activity_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cmpd_activity_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cmpd_activity_type`
--

LOCK TABLES `cmpd_activity_type` WRITE;
/*!40000 ALTER TABLE `cmpd_activity_type` DISABLE KEYS */;
INSERT INTO `cmpd_activity_type` VALUES ('ChEMBL','A manually curated chemical database of bioactive molecules with drug-like properties. It is maintained by the European Bioinformatics Institute (EBI), of the European Molecular Biology Laboratory (EMBL), based at the Wellcome Trust Genome Campus, Hinxton, UK.'),('Guide to Pharmacology','The IUPHAR/BPS Guide to PHARMACOLOGY');
/*!40000 ALTER TABLE `cmpd_activity_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compartment`
--

DROP TABLE IF EXISTS `compartment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compartment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ctype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `target_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `go_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `go_term` text COLLATE utf8_unicode_ci,
  `evidence` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `zscore` decimal(4,3) DEFAULT NULL,
  `conf` decimal(2,1) DEFAULT NULL,
  `url` text COLLATE utf8_unicode_ci,
  `reliability` enum('Supported','Approved','Validated') COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `compartment_idx1` (`ctype`),
  KEY `compartment_idx2` (`target_id`),
  KEY `compartment_idx3` (`protein_id`),
  CONSTRAINT `fk_compartment__compartment_type` FOREIGN KEY (`ctype`) REFERENCES `compartment_type` (`name`),
  CONSTRAINT `fk_compartment_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_compartment_target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compartment`
--

LOCK TABLES `compartment` WRITE;
/*!40000 ALTER TABLE `compartment` DISABLE KEYS */;
/*!40000 ALTER TABLE `compartment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compartment_type`
--

DROP TABLE IF EXISTS `compartment_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `compartment_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compartment_type`
--

LOCK TABLES `compartment_type` WRITE;
/*!40000 ALTER TABLE `compartment_type` DISABLE KEYS */;
INSERT INTO `compartment_type` VALUES ('Human Cell Atlas','Human Cell Atlas protein locations, minus rows with Uncertain reliability.'),('JensenLab Experiment','Experiment channel subcellular locations from JensenLab COMPARTMENTS resource, filtered for confidence scores of 3 or greater.'),('JensenLab Knowledge','Knowledge channel subcellular locations from JensenLab COMPARTMENTS resource, filtered for confidence scores of 3 or greater.'),('JensenLab Prediction','Prediction channel subcellular locations from JensenLab COMPARTMENTS resource, filtered for confidence scores of 3 or greater.'),('JensenLab Text Mining','Text Mining channel subcellular locations from JensenLab COMPARTMENTS resource, filtered for zscore of 3.0 or greater.');
/*!40000 ALTER TABLE `compartment_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `data_type`
--

DROP TABLE IF EXISTS `data_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `data_type` (
  `name` varchar(7) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data_type`
--

LOCK TABLES `data_type` WRITE;
/*!40000 ALTER TABLE `data_type` DISABLE KEYS */;
INSERT INTO `data_type` VALUES ('Boolean'),('Date'),('Integer'),('Number'),('String');
/*!40000 ALTER TABLE `data_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dataset`
--

DROP TABLE IF EXISTS `dataset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dataset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `source` text COLLATE utf8_unicode_ci NOT NULL,
  `app` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `app_version` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `url` text COLLATE utf8_unicode_ci,
  `comments` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dataset`
--

LOCK TABLES `dataset` WRITE;
/*!40000 ALTER TABLE `dataset` DISABLE KEYS */;
/*!40000 ALTER TABLE `dataset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dbinfo`
--

DROP TABLE IF EXISTS `dbinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dbinfo` (
  `dbname` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `schema_ver` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `data_ver` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `owner` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `is_copy` tinyint(1) NOT NULL DEFAULT '0',
  `dump_file` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dbinfo`
--

LOCK TABLES `dbinfo` WRITE;
/*!40000 ALTER TABLE `dbinfo` DISABLE KEYS */;
INSERT INTO `dbinfo` VALUES ('tcrd7','7.0.0','0.0.0','smathias',0,NULL);
/*!40000 ALTER TABLE `dbinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disease`
--

DROP TABLE IF EXISTS `disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disease` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dtype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `nhprotein_id` int(11) DEFAULT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `did` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `evidence` text COLLATE utf8_unicode_ci,
  `zscore` decimal(4,3) DEFAULT NULL,
  `conf` decimal(2,1) DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `reference` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `drug_name` text COLLATE utf8_unicode_ci,
  `log2foldchange` decimal(5,3) DEFAULT NULL,
  `pvalue` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `score` decimal(16,15) DEFAULT NULL,
  `source` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `O2S` decimal(16,13) DEFAULT NULL,
  `S2O` decimal(16,13) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `disease_idx1` (`dtype`),
  KEY `disease_idx2` (`protein_id`),
  KEY `disease_idx3` (`nhprotein_id`),
  CONSTRAINT `fk_disease__disease_type` FOREIGN KEY (`dtype`) REFERENCES `disease_type` (`name`),
  CONSTRAINT `fk_disease_nhprotein` FOREIGN KEY (`nhprotein_id`) REFERENCES `nhprotein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_disease_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease`
--

LOCK TABLES `disease` WRITE;
/*!40000 ALTER TABLE `disease` DISABLE KEYS */;
/*!40000 ALTER TABLE `disease` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `disease_type`
--

DROP TABLE IF EXISTS `disease_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `disease_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `disease_type`
--

LOCK TABLES `disease_type` WRITE;
/*!40000 ALTER TABLE `disease_type` DISABLE KEYS */;
INSERT INTO `disease_type` VALUES ('CTD','Gene-Disease associations with direct evidence from the Comparative Toxicogenomics Database.'),('DisGeNET','Currated disease associations from DisGeNET (http://www.disgenet.org/)'),('DrugCentral Indication','Disease indications and associated drug names from Drug Central.'),('eRAM','\"Currated gene\" disease associations from eRAM'),('Expression Atlas','Target-Disease associations from Expression Atlas where the log2 fold change in gene expresion in disease sample vs reference sample is greater than 1.0. Only reference samples \"normal\" or \"healthy\" are selected. Data is derived from the file: ftp://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/atlas-latest-data.tar.gz'),('JensenLab Experiment COSMIC','JensenLab Experiment channel using COSMIC'),('JensenLab Experiment DistiLD','JensenLab Experiment channel using DistiLD'),('JensenLab Knowledge GHR','JensenLab Knowledge channel using GHR'),('JensenLab Knowledge UniProtKB-KW','JensenLab Knowledge channel using UniProtKB-KW'),('JensenLab Text Mining','JensenLab Text Mining channel'),('Monarch','Gene-Disease associations from Monarch that have S2O and/or O2S score(s)'),('UniProt','Disease association from UniProt comment field with type=\"disease\"');
/*!40000 ALTER TABLE `disease_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `do`
--

DROP TABLE IF EXISTS `do`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `do` (
  `doid` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `def` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`doid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `do`
--

LOCK TABLES `do` WRITE;
/*!40000 ALTER TABLE `do` DISABLE KEYS */;
/*!40000 ALTER TABLE `do` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `do_parent`
--

DROP TABLE IF EXISTS `do_parent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `do_parent` (
  `doid` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  KEY `fk_do_parent__do` (`doid`),
  CONSTRAINT `fk_do_parent__do` FOREIGN KEY (`doid`) REFERENCES `do` (`doid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `do_parent`
--

LOCK TABLES `do_parent` WRITE;
/*!40000 ALTER TABLE `do_parent` DISABLE KEYS */;
/*!40000 ALTER TABLE `do_parent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `do_xref`
--

DROP TABLE IF EXISTS `do_xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `do_xref` (
  `doid` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `db` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`doid`,`db`,`value`),
  KEY `do_xref__idx2` (`db`,`value`),
  CONSTRAINT `fk_do_xref__do` FOREIGN KEY (`doid`) REFERENCES `do` (`doid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `do_xref`
--

LOCK TABLES `do_xref` WRITE;
/*!40000 ALTER TABLE `do_xref` DISABLE KEYS */;
/*!40000 ALTER TABLE `do_xref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drgc_resource`
--

DROP TABLE IF EXISTS `drgc_resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `drgc_resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `resource_type` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `json` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `drgc_resource_idx1` (`target_id`),
  CONSTRAINT `fk_drgc_resource__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drgc_resource`
--

LOCK TABLES `drgc_resource` WRITE;
/*!40000 ALTER TABLE `drgc_resource` DISABLE KEYS */;
/*!40000 ALTER TABLE `drgc_resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drug_activity`
--

DROP TABLE IF EXISTS `drug_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `drug_activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `drug` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `act_value` decimal(10,8) DEFAULT NULL,
  `act_type` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `action_type` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `has_moa` tinyint(1) NOT NULL,
  `source` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reference` text COLLATE utf8_unicode_ci,
  `smiles` text COLLATE utf8_unicode_ci,
  `cmpd_chemblid` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `nlm_drug_info` text COLLATE utf8_unicode_ci,
  `cmpd_pubchem_cid` int(11) DEFAULT NULL,
  `dcid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `drug_activity_idx1` (`target_id`),
  CONSTRAINT `fk_drug_activity__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drug_activity`
--

LOCK TABLES `drug_activity` WRITE;
/*!40000 ALTER TABLE `drug_activity` DISABLE KEYS */;
/*!40000 ALTER TABLE `drug_activity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dto`
--

DROP TABLE IF EXISTS `dto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dto` (
  `dtoid` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `def` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`dtoid`),
  KEY `dto_idx1` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dto`
--

LOCK TABLES `dto` WRITE;
/*!40000 ALTER TABLE `dto` DISABLE KEYS */;
/*!40000 ALTER TABLE `dto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expression`
--

DROP TABLE IF EXISTS `expression`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expression` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `etype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `target_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `tissue` text COLLATE utf8_unicode_ci NOT NULL,
  `qual_value` enum('Not detected','Low','Medium','High') COLLATE utf8_unicode_ci DEFAULT NULL,
  `number_value` decimal(12,6) DEFAULT NULL,
  `boolean_value` tinyint(1) DEFAULT NULL,
  `string_value` text COLLATE utf8_unicode_ci,
  `pubmed_id` int(11) DEFAULT NULL,
  `evidence` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `zscore` decimal(4,3) DEFAULT NULL,
  `conf` decimal(2,1) DEFAULT NULL,
  `oid` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `confidence` tinyint(1) DEFAULT NULL,
  `url` text COLLATE utf8_unicode_ci,
  `cell_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `uberon_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `expression_idx1` (`etype`),
  KEY `expression_idx2` (`target_id`),
  KEY `expression_idx3` (`protein_id`),
  KEY `fk_expression_uberon` (`uberon_id`),
  CONSTRAINT `fk_expression__expression_type` FOREIGN KEY (`etype`) REFERENCES `expression_type` (`name`),
  CONSTRAINT `fk_expression__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_expression__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_expression_uberon` FOREIGN KEY (`uberon_id`) REFERENCES `uberon` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expression`
--

LOCK TABLES `expression` WRITE;
/*!40000 ALTER TABLE `expression` DISABLE KEYS */;
/*!40000 ALTER TABLE `expression` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expression_type`
--

DROP TABLE IF EXISTS `expression_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `expression_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `data_type` varchar(7) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`),
  UNIQUE KEY `expression_type_idx1` (`name`,`data_type`),
  KEY `fk_expression_type__data_type` (`data_type`),
  CONSTRAINT `fk_expression_type__data_type` FOREIGN KEY (`data_type`) REFERENCES `data_type` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expression_type`
--

LOCK TABLES `expression_type` WRITE;
/*!40000 ALTER TABLE `expression_type` DISABLE KEYS */;
INSERT INTO `expression_type` VALUES ('CCLE','Number','Broad Institute Cancer Cell Line Encyclopedia expression data.'),('Cell Surface Protein Atlas','Boolean','Cell Surface Protein Atlas protein expression in cell lines.'),('Consensus','String','Qualitative consensus expression value calulated from GTEx, HPA and HPM data aggregated according to manually mapped tissue types.'),('GTEx','Number','GTEx V4 RNA-SeQCv1.1.8 Log Median RPKM and qualitative expression values per SMTSD tissue type.'),('HCA RNA','Number','Human Cell Atlas gene expression in cell lines.'),('HPA','String','Human Protein Atlas normal tissue expression values.'),('HPM Gene','Number','Human Proteome Map gene-level Log and qualitative expression values.'),('HPM Protein','Number','Human Proteome Map protein-level Log and qualitative expression values.'),('JensenLab Experiment Cardiac proteome','String','JensenLab Experiment channel using Cardiac proteome'),('JensenLab Experiment Exon array','String','JensenLab Experiment channel using Exon array'),('JensenLab Experiment GNF','String','JensenLab Experiment channel using GNF'),('JensenLab Experiment HPA','String','JensenLab Experiment channel using Human Protein Atlas IHC'),('JensenLab Experiment HPA-RNA','String','JensenLab Experiment channel using Human Protein Atlas RNA'),('JensenLab Experiment HPM','String','JensenLab Experiment channel using Humap Proteome Map'),('JensenLab Experiment RNA-seq','String','JensenLab Experiment channel using RNA-seq'),('JensenLab Experiment UniGene','String','JensenLab Experiment channel using UniGene'),('JensenLab Knowledge UniProtKB-RC','Boolean','JensenLab Knowledge channel using UniProtKB-RC'),('JensenLab Text Mining','Boolean','JensenLab Text Mining channel'),('UniProt Tissue','Boolean','Tissue and PubMed ID from UniProt');
/*!40000 ALTER TABLE `expression_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feature`
--

DROP TABLE IF EXISTS `feature`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feature` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `type` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `srcid` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `evidence` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `begin` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `original` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `variation` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `feature_idx1` (`protein_id`),
  CONSTRAINT `fk_feature_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feature`
--

LOCK TABLES `feature` WRITE;
/*!40000 ALTER TABLE `feature` DISABLE KEYS */;
/*!40000 ALTER TABLE `feature` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gene_attribute`
--

DROP TABLE IF EXISTS `gene_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_attribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `gat_id` int(11) NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `value` int(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `gene_attribute_idx1` (`protein_id`),
  KEY `gene_attribute_idx2` (`gat_id`),
  CONSTRAINT `fk_gene_attribute__gene_attribute_type` FOREIGN KEY (`gat_id`) REFERENCES `gene_attribute_type` (`id`),
  CONSTRAINT `fk_gene_attribute__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gene_attribute`
--

LOCK TABLES `gene_attribute` WRITE;
/*!40000 ALTER TABLE `gene_attribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `gene_attribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gene_attribute_type`
--

DROP TABLE IF EXISTS `gene_attribute_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gene_attribute_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `association` text COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `resource_group` enum('omics','genomics','proteomics','physical interactions','transcriptomics','structural or functional annotations','disease or phenotype associations') COLLATE utf8_unicode_ci NOT NULL,
  `measurement` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `attribute_group` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `attribute_type` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `pubmed_ids` text COLLATE utf8_unicode_ci,
  `url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `gene_attribute_type_idx1` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gene_attribute_type`
--

LOCK TABLES `gene_attribute_type` WRITE;
/*!40000 ALTER TABLE `gene_attribute_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `gene_attribute_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `generif`
--

DROP TABLE IF EXISTS `generif`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `generif` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `pubmed_ids` text COLLATE utf8_unicode_ci,
  `text` text COLLATE utf8_unicode_ci NOT NULL,
  `years` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `generif_idx1` (`protein_id`),
  CONSTRAINT `fk_generif_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `generif`
--

LOCK TABLES `generif` WRITE;
/*!40000 ALTER TABLE `generif` DISABLE KEYS */;
/*!40000 ALTER TABLE `generif` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goa`
--

DROP TABLE IF EXISTS `goa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `goa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `go_id` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `go_term` text COLLATE utf8_unicode_ci,
  `evidence` text COLLATE utf8_unicode_ci,
  `goeco` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `assigned_by` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `goa_idx1` (`protein_id`),
  CONSTRAINT `fk_goa_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goa`
--

LOCK TABLES `goa` WRITE;
/*!40000 ALTER TABLE `goa` DISABLE KEYS */;
/*!40000 ALTER TABLE `goa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gtex`
--

DROP TABLE IF EXISTS `gtex`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gtex` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) DEFAULT NULL,
  `tissue` text COLLATE utf8_unicode_ci NOT NULL,
  `gender` enum('F','M') COLLATE utf8_unicode_ci NOT NULL,
  `tpm` decimal(12,6) NOT NULL,
  `tpm_rank` decimal(4,3) DEFAULT NULL,
  `tpm_rank_bysex` decimal(4,3) DEFAULT NULL,
  `tpm_level` enum('Not detected','Low','Medium','High') COLLATE utf8_unicode_ci NOT NULL,
  `tpm_level_bysex` enum('Not detected','Low','Medium','High') COLLATE utf8_unicode_ci DEFAULT NULL,
  `tpm_f` decimal(12,6) DEFAULT NULL,
  `tpm_m` decimal(12,6) DEFAULT NULL,
  `log2foldchange` decimal(4,3) DEFAULT NULL,
  `tau` decimal(4,3) DEFAULT NULL,
  `tau_bysex` decimal(4,3) DEFAULT NULL,
  `uberon_id` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `expression_idx1` (`protein_id`),
  CONSTRAINT `fk_gtex_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gtex`
--

LOCK TABLES `gtex` WRITE;
/*!40000 ALTER TABLE `gtex` DISABLE KEYS */;
/*!40000 ALTER TABLE `gtex` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gwas`
--

DROP TABLE IF EXISTS `gwas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gwas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `disease_trait` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `snps` text COLLATE utf8_unicode_ci,
  `pmid` int(11) DEFAULT NULL,
  `study` text COLLATE utf8_unicode_ci,
  `context` text COLLATE utf8_unicode_ci,
  `intergenic` tinyint(1) DEFAULT NULL,
  `p_value` double DEFAULT NULL,
  `or_beta` float DEFAULT NULL,
  `cnv` char(1) COLLATE utf8_unicode_ci DEFAULT NULL,
  `mapped_trait` text COLLATE utf8_unicode_ci,
  `mapped_trait_uri` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `gwas_idx1` (`protein_id`),
  CONSTRAINT `fk_gwas_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gwas`
--

LOCK TABLES `gwas` WRITE;
/*!40000 ALTER TABLE `gwas` DISABLE KEYS */;
/*!40000 ALTER TABLE `gwas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `hgram_cdf`
--

DROP TABLE IF EXISTS `hgram_cdf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hgram_cdf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `type` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `attr_count` int(11) NOT NULL,
  `attr_cdf` decimal(17,16) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `hgram_cdf_idx1` (`protein_id`),
  KEY `hgram_cdf_idx2` (`type`),
  CONSTRAINT `fk_hgram_cdf__gene_attribute_type` FOREIGN KEY (`type`) REFERENCES `gene_attribute_type` (`name`),
  CONSTRAINT `fk_hgram_cdf__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hgram_cdf`
--

LOCK TABLES `hgram_cdf` WRITE;
/*!40000 ALTER TABLE `hgram_cdf` DISABLE KEYS */;
/*!40000 ALTER TABLE `hgram_cdf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `homologene`
--

DROP TABLE IF EXISTS `homologene`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `homologene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) DEFAULT NULL,
  `nhprotein_id` int(11) DEFAULT NULL,
  `groupid` int(11) NOT NULL,
  `taxid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `homologene_idx1` (`protein_id`),
  KEY `homologene_idx2` (`nhprotein_id`),
  CONSTRAINT `fk_homologene_nhprotein` FOREIGN KEY (`nhprotein_id`) REFERENCES `nhprotein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_homologene_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `homologene`
--

LOCK TABLES `homologene` WRITE;
/*!40000 ALTER TABLE `homologene` DISABLE KEYS */;
/*!40000 ALTER TABLE `homologene` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idg_evol`
--

DROP TABLE IF EXISTS `idg_evol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `idg_evol` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tcrd_ver` tinyint(1) NOT NULL,
  `tcrd_dbid` int(11) NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `uniprot` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `sym` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `geneid` int(11) DEFAULT NULL,
  `tdl` varchar(6) COLLATE utf8_unicode_ci NOT NULL,
  `fam` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idg_evol_idx1` (`uniprot`),
  KEY `idg_evol_idx2` (`sym`),
  KEY `idg_evol_idx3` (`geneid`),
  KEY `idg_evol_idx4` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idg_evol`
--

LOCK TABLES `idg_evol` WRITE;
/*!40000 ALTER TABLE `idg_evol` DISABLE KEYS */;
/*!40000 ALTER TABLE `idg_evol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `info_type`
--

DROP TABLE IF EXISTS `info_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `info_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `data_type` varchar(7) COLLATE utf8_unicode_ci NOT NULL,
  `unit` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`),
  UNIQUE KEY `info_type_idx1` (`name`,`data_type`),
  UNIQUE KEY `expression_type_idx1` (`name`,`data_type`),
  KEY `fk_info_type__data_type` (`data_type`),
  CONSTRAINT `fk_info_type__data_type` FOREIGN KEY (`data_type`) REFERENCES `data_type` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `info_type`
--

LOCK TABLES `info_type` WRITE;
/*!40000 ALTER TABLE `info_type` DISABLE KEYS */;
INSERT INTO `info_type` VALUES ('Ab Count','Integer',NULL,'Antibody count from antibodypedia.com'),('Antibodypedia.com URL','String',NULL,'Antibodypedia.com detail page URL for a given protein.'),('ChEMBL Activity Count','Integer',NULL,'Number of filtered bioactivities in ChEMBL better than 1uM (10uM for Ion Channels)'),('ChEMBL First Reference Year','Integer',NULL,'The year of the oldest bioactivity reference this target has in ChEMBL. Note that this is derived from ChEMBL activities as filtered for TCRD purposes.'),('ChEMBL Selective Compound','String',NULL,'2 log selective compound on this target. Value is ChEMBL ID and SMILES joined with a pipe character.'),('Drugable Epigenome Class','String',NULL,'Drugable Epigenome Class/Domain from Nature Reviews Drug Discovery 11, 384-400 (May 2012)'),('DrugDB Count','Integer',NULL,'Number of drugs in DrugDB with with activity better than 1uM (10uM for Ion Channels)'),('EBI Total Patent Count','Integer',NULL,'Total count of all patents mentioning this protein according to EBI text mining'),('EBI Total Patent Count (Relevant)','Integer',NULL,'Total count of all relevant patents mentioning this protein according to EBI text mining'),('Experimental MF/BP Leaf Term GOA','String',NULL,'Indicates that a target is annotated with one or more GO MF/BP leaf term with Experimental Evidence code. Value is a concatenation of all GO terms/names/evidences.'),('GTEx Tissue Specificity Index','Number',NULL,'Tau as defined in Yanai, I. et. al., Bioinformatics 21(5): 650-659 (2005) calculated on GTEx data.'),('Has MLP Assay','Boolean',NULL,'Indicates that a protein is used in at least one PubChem MLP assay. Details are in mlp_assay_info tabel.'),('HPA Tissue Specificity Index','Number',NULL,'Tau as defined in Yanai, I. et. al., Bioinformatics 21(5): 650-659 (2005) calculated on HPA Protein data.'),('HPM Gene Tissue Specificity Index','Number',NULL,'Tau as defined in Yanai, I. et. al., Bioinformatics 21(5): 650-659 (2005) calculated on HPM Gene data.'),('HPM Protein Tissue Specificity Index','Number',NULL,'Tau as defined in Yanai, I. et. al., Bioinformatics 21(5): 650-659 (2005) calculated on HPM Protein data.'),('IMPC Clones','String',NULL,'#Clones from IMPC Spreadsheet'),('IMPC Status','String',NULL,'Best Status from IMPC Spreadsheet'),('Is Transcription Factor','Boolean',NULL,'Target is a transcription factor according to http://www.bioguo.org/AnimalTFDB'),('JensenLab COMPARTMENT Prediction Plasma membrane','String',NULL,'Prediction method and value (conf 2 or 3 only) that the protein is Plasma membrane from JensenLab COMPARTMENTS resouce'),('JensenLab PubMed Score','Number',NULL,'PubMed paper count from textmining done in group of Lars-Juhl Jensen.'),('MAb Count','Integer',NULL,'Monoclonal Antibody count from antibodypedia.com'),('NCBI Gene PubMed Count','Integer',NULL,'Number of PubMed references for target and all its aliases'),('NCBI Gene Summary','String',NULL,'Gene summary statement from NCBI Gene database'),('PubTator Score','Number',NULL,'PubMed paper count from PubTator data run through Lars Jensen\'s counting proceedure'),('TIN-X Novelty Score','Number',NULL,'TIN-X novelty score from Cristian Bologa.'),('TM Count','Integer',NULL,'Number of transmembrane helices according to Survey of the Human Transmembrane Proteome (https://modbase.compbio.ucsf.edu/projects/membrane/). At least 2 are required to be in their list.'),('TMHMM Prediction','String',NULL,'Short output from TMHMM run locally on protein sequences.'),('UniProt Function','String',NULL,'Funtion comment from UniProt');
/*!40000 ALTER TABLE `info_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kegg_distance`
--

DROP TABLE IF EXISTS `kegg_distance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kegg_distance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pid1` int(11) NOT NULL,
  `pid2` int(11) NOT NULL,
  `distance` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `kegg_distance_idx1` (`pid1`),
  KEY `kegg_distance_idx2` (`pid2`),
  CONSTRAINT `fk_kegg_distance__protein1` FOREIGN KEY (`pid1`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_kegg_distance__protein2` FOREIGN KEY (`pid2`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kegg_distance`
--

LOCK TABLES `kegg_distance` WRITE;
/*!40000 ALTER TABLE `kegg_distance` DISABLE KEYS */;
/*!40000 ALTER TABLE `kegg_distance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kegg_nearest_tclin`
--

DROP TABLE IF EXISTS `kegg_nearest_tclin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kegg_nearest_tclin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `tclin_id` int(11) NOT NULL,
  `direction` enum('upstream','downstream') COLLATE utf8_unicode_ci NOT NULL,
  `distance` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `kegg_nearest_tclin_idx1` (`protein_id`),
  KEY `kegg_nearest_tclin_idx2` (`tclin_id`),
  CONSTRAINT `fk_kegg_nearest_tclin__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_kegg_nearest_tclin__target` FOREIGN KEY (`tclin_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kegg_nearest_tclin`
--

LOCK TABLES `kegg_nearest_tclin` WRITE;
/*!40000 ALTER TABLE `kegg_nearest_tclin` DISABLE KEYS */;
/*!40000 ALTER TABLE `kegg_nearest_tclin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lincs`
--

DROP TABLE IF EXISTS `lincs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lincs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `cellid` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `zscore` decimal(8,6) NOT NULL,
  `pert_dcid` int(11) NOT NULL,
  `pert_smiles` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `lincs_idx1` (`protein_id`),
  CONSTRAINT `fk_lincs_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lincs`
--

LOCK TABLES `lincs` WRITE;
/*!40000 ALTER TABLE `lincs` DISABLE KEYS */;
/*!40000 ALTER TABLE `lincs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locsig`
--

DROP TABLE IF EXISTS `locsig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `locsig` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `location` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `signal` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `pmids` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `compartment_idx1` (`protein_id`),
  CONSTRAINT `fk_locsig_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locsig`
--

LOCK TABLES `locsig` WRITE;
/*!40000 ALTER TABLE `locsig` DISABLE KEYS */;
/*!40000 ALTER TABLE `locsig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mlp_assay_info`
--

DROP TABLE IF EXISTS `mlp_assay_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mlp_assay_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `assay_name` text COLLATE utf8_unicode_ci NOT NULL,
  `method` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `active_sids` int(11) DEFAULT NULL,
  `inactive_sids` int(11) DEFAULT NULL,
  `iconclusive_sids` int(11) DEFAULT NULL,
  `total_sids` int(11) DEFAULT NULL,
  `aid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mlp_assay_info_idx1` (`protein_id`),
  CONSTRAINT `fk_mai_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mlp_assay_info`
--

LOCK TABLES `mlp_assay_info` WRITE;
/*!40000 ALTER TABLE `mlp_assay_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `mlp_assay_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mpo`
--

DROP TABLE IF EXISTS `mpo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mpo` (
  `mpid` char(10) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `def` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`mpid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mpo`
--

LOCK TABLES `mpo` WRITE;
/*!40000 ALTER TABLE `mpo` DISABLE KEYS */;
/*!40000 ALTER TABLE `mpo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nhprotein`
--

DROP TABLE IF EXISTS `nhprotein`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `nhprotein` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uniprot` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `sym` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `species` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `taxid` int(11) NOT NULL,
  `geneid` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nhprotein_idx1` (`uniprot`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `nhprotein`
--

LOCK TABLES `nhprotein` WRITE;
/*!40000 ALTER TABLE `nhprotein` DISABLE KEYS */;
/*!40000 ALTER TABLE `nhprotein` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `omim`
--

DROP TABLE IF EXISTS `omim`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `omim` (
  `mim` int(11) NOT NULL,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`mim`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `omim`
--

LOCK TABLES `omim` WRITE;
/*!40000 ALTER TABLE `omim` DISABLE KEYS */;
/*!40000 ALTER TABLE `omim` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `omim_ps`
--

DROP TABLE IF EXISTS `omim_ps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `omim_ps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `omim_ps_id` char(8) COLLATE utf8_unicode_ci NOT NULL,
  `mim` int(11) DEFAULT NULL,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_omim_ps__omim` (`mim`),
  CONSTRAINT `fk_omim_ps__omim` FOREIGN KEY (`mim`) REFERENCES `omim` (`mim`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `omim_ps`
--

LOCK TABLES `omim_ps` WRITE;
/*!40000 ALTER TABLE `omim_ps` DISABLE KEYS */;
/*!40000 ALTER TABLE `omim_ps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ortholog`
--

DROP TABLE IF EXISTS `ortholog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ortholog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `taxid` int(11) NOT NULL,
  `species` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `db_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `geneid` int(11) DEFAULT NULL,
  `symbol` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `mod_url` text COLLATE utf8_unicode_ci,
  `sources` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ortholog_idx1` (`protein_id`),
  CONSTRAINT `fk_ortholog_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ortholog`
--

LOCK TABLES `ortholog` WRITE;
/*!40000 ALTER TABLE `ortholog` DISABLE KEYS */;
/*!40000 ALTER TABLE `ortholog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ortholog_disease`
--

DROP TABLE IF EXISTS `ortholog_disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ortholog_disease` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `did` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `ortholog_id` int(11) NOT NULL,
  `score` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ortholog_disease_idx1` (`protein_id`),
  KEY `ortholog_disease_idx2` (`ortholog_id`),
  CONSTRAINT `fk_ortholog_disease__ortholog` FOREIGN KEY (`ortholog_id`) REFERENCES `ortholog` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ortholog_disease__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ortholog_disease`
--

LOCK TABLES `ortholog_disease` WRITE;
/*!40000 ALTER TABLE `ortholog_disease` DISABLE KEYS */;
/*!40000 ALTER TABLE `ortholog_disease` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `p2pc`
--

DROP TABLE IF EXISTS `p2pc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `p2pc` (
  `panther_class_id` int(11) NOT NULL,
  `protein_id` int(11) NOT NULL,
  KEY `p2pc_idx1` (`panther_class_id`),
  KEY `p2pc_idx2` (`protein_id`),
  CONSTRAINT `fk_p2pc__panther_class` FOREIGN KEY (`panther_class_id`) REFERENCES `panther_class` (`id`),
  CONSTRAINT `fk_p2pc_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `p2pc`
--

LOCK TABLES `p2pc` WRITE;
/*!40000 ALTER TABLE `p2pc` DISABLE KEYS */;
/*!40000 ALTER TABLE `p2pc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `panther_class`
--

DROP TABLE IF EXISTS `panther_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `panther_class` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pcid` char(7) COLLATE utf8_unicode_ci NOT NULL,
  `parent_pcids` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `panther_class_idx1` (`pcid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `panther_class`
--

LOCK TABLES `panther_class` WRITE;
/*!40000 ALTER TABLE `panther_class` DISABLE KEYS */;
/*!40000 ALTER TABLE `panther_class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patent_count`
--

DROP TABLE IF EXISTS `patent_count`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `patent_count` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `year` int(4) NOT NULL,
  `count` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `patent_count_idx1` (`protein_id`),
  CONSTRAINT `fk_patent_count__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patent_count`
--

LOCK TABLES `patent_count` WRITE;
/*!40000 ALTER TABLE `patent_count` DISABLE KEYS */;
/*!40000 ALTER TABLE `patent_count` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pathway`
--

DROP TABLE IF EXISTS `pathway`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pathway` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `pwtype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `id_in_source` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `pathway_idx1` (`target_id`),
  KEY `pathway_idx2` (`protein_id`),
  KEY `pathway_idx3` (`pwtype`),
  CONSTRAINT `fk_pathway__pathway_type` FOREIGN KEY (`pwtype`) REFERENCES `pathway_type` (`name`),
  CONSTRAINT `fk_pathway_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pathway_target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pathway`
--

LOCK TABLES `pathway` WRITE;
/*!40000 ALTER TABLE `pathway` DISABLE KEYS */;
/*!40000 ALTER TABLE `pathway` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pathway_type`
--

DROP TABLE IF EXISTS `pathway_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pathway_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pathway_type`
--

LOCK TABLES `pathway_type` WRITE;
/*!40000 ALTER TABLE `pathway_type` DISABLE KEYS */;
INSERT INTO `pathway_type` VALUES ('KEGG','http://www.kegg.jp/kegg/pathway.html'),('PathwayCommons: ctd','http://www.pathwaycommons.org/pc2/ctd'),('PathwayCommons: humancyc','http://www.pathwaycommons.org/pc2/humancyc'),('PathwayCommons: inoh','http://www.pathwaycommons.org/pc2/inoh'),('PathwayCommons: mirtarbase','http://www.pathwaycommons.org/pc2/mirtarbase'),('PathwayCommons: netpath','http://www.pathwaycommons.org/pc2/netpath'),('PathwayCommons: panther','http://pathwaycommons.org/pc2/panther'),('PathwayCommons: pid','http://www.pathwaycommons.org/pc2/pid'),('PathwayCommons: recon','http://www.pathwaycommons.org/pc2/recon'),('PathwayCommons: smpdb','http://www.pathwaycommons.org/pc2/smpdb'),('PathwayCommons: transfac','http://www.pathwaycommons.org/pc2/transfac'),('Reactome','http://www.reactome.org/'),('UniProt','http://www.uniprot.org/'),('WikiPathways','http://www.wikipathways.org/index.php/WikiPathways');
/*!40000 ALTER TABLE `pathway_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phenotype`
--

DROP TABLE IF EXISTS `phenotype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phenotype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ptype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `nhprotein_id` int(11) DEFAULT NULL,
  `trait` text COLLATE utf8_unicode_ci,
  `top_level_term_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `top_level_term_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `term_id` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `term_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `term_description` text COLLATE utf8_unicode_ci,
  `p_value` double DEFAULT NULL,
  `percentage_change` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `effect_size` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `procedure_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `parameter_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gp_assoc` tinyint(1) DEFAULT NULL,
  `statistical_method` text COLLATE utf8_unicode_ci,
  `sex` varchar(8) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `phenotype_idx1` (`ptype`),
  KEY `phenotype_idx2` (`protein_id`),
  KEY `phenotype_idx3` (`nhprotein_id`),
  CONSTRAINT `fk_phenotype__phenotype_type` FOREIGN KEY (`ptype`) REFERENCES `phenotype_type` (`name`),
  CONSTRAINT `fk_phenotype_nhprotein` FOREIGN KEY (`nhprotein_id`) REFERENCES `nhprotein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_phenotype_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phenotype`
--

LOCK TABLES `phenotype` WRITE;
/*!40000 ALTER TABLE `phenotype` DISABLE KEYS */;
/*!40000 ALTER TABLE `phenotype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phenotype_type`
--

DROP TABLE IF EXISTS `phenotype_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phenotype_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `ontology` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`),
  UNIQUE KEY `phenotype_type_idx1` (`name`,`ontology`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phenotype_type`
--

LOCK TABLES `phenotype_type` WRITE;
/*!40000 ALTER TABLE `phenotype_type` DISABLE KEYS */;
INSERT INTO `phenotype_type` VALUES ('GWAS Catalog',NULL,'GWAS findings from NHGRI/EBI GWAS catalog file.'),('IMPC','Mammalian Phenotype Ontology','Phenotypes from the International Mouse Phenotyping Consortium. These are single gene knockout phenotypes.'),('JAX/MGI Human Ortholog Phenotype','Mammalian Phenotype Ontology','JAX/MGI house/human orthology phenotypes in file HMD_HumanPhenotype.rpt from ftp.informatics.jax.or'),('OMIM',NULL,'Phenotypes from OMIM with status Confirmed. phenotype.trait is a concatenation of Title, MIM Number, Method, and Comments fields from the OMIM genemap2.txt file.');
/*!40000 ALTER TABLE `phenotype_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pmscore`
--

DROP TABLE IF EXISTS `pmscore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pmscore` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `year` int(4) NOT NULL,
  `score` decimal(12,6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `pmscore_idx1` (`protein_id`),
  CONSTRAINT `fk_pmscore_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pmscore`
--

LOCK TABLES `pmscore` WRITE;
/*!40000 ALTER TABLE `pmscore` DISABLE KEYS */;
/*!40000 ALTER TABLE `pmscore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ppi`
--

DROP TABLE IF EXISTS `ppi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ppi` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ppitype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `protein1_id` int(11) NOT NULL,
  `protein1_str` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `protein2_id` int(11) NOT NULL,
  `protein2_str` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `p_int` decimal(10,9) DEFAULT NULL,
  `p_ni` decimal(10,9) DEFAULT NULL,
  `p_wrong` decimal(10,9) DEFAULT NULL,
  `evidence` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `interaction_type` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `score` int(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ppi_idx1` (`protein1_id`),
  KEY `ppi_idx2` (`protein2_id`),
  KEY `ppi_idx3` (`ppitype`),
  CONSTRAINT `fk_ppi_protein1` FOREIGN KEY (`protein1_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ppi_protein2` FOREIGN KEY (`protein2_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ppi`
--

LOCK TABLES `ppi` WRITE;
/*!40000 ALTER TABLE `ppi` DISABLE KEYS */;
/*!40000 ALTER TABLE `ppi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ppi_type`
--

DROP TABLE IF EXISTS `ppi_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ppi_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ppi_type`
--

LOCK TABLES `ppi_type` WRITE;
/*!40000 ALTER TABLE `ppi_type` DISABLE KEYS */;
INSERT INTO `ppi_type` VALUES ('BioPlex','The BioPlex (biophysical interactions of ORFeome-based complexes) network is the result of creating thousands of cell lines with each expressing a tagged version of a protein from the ORFeome collection.','http://wren.hms.harvard.edu/bioplex/'),('Reactome','Interactions derived from Reactome pathways','http://www.reactome.org/');
/*!40000 ALTER TABLE `ppi_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `protein`
--

DROP TABLE IF EXISTS `protein`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `protein` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci NOT NULL,
  `uniprot` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `up_version` int(11) DEFAULT NULL,
  `geneid` int(11) DEFAULT NULL,
  `sym` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `family` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `chr` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `seq` text COLLATE utf8_unicode_ci,
  `dtoid` varchar(13) COLLATE utf8_unicode_ci DEFAULT NULL,
  `stringid` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dtoclass` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `protein_idx1` (`uniprot`),
  UNIQUE KEY `protein_idx2` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `protein`
--

LOCK TABLES `protein` WRITE;
/*!40000 ALTER TABLE `protein` DISABLE KEYS */;
/*!40000 ALTER TABLE `protein` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `protein2pubmed`
--

DROP TABLE IF EXISTS `protein2pubmed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `protein2pubmed` (
  `protein_id` int(11) NOT NULL,
  `pubmed_id` int(11) NOT NULL,
  KEY `protein2pubmed_idx1` (`protein_id`),
  KEY `protein2pubmed_idx2` (`pubmed_id`),
  CONSTRAINT `fk_protein2pubmed__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_protein2pubmed__pubmed` FOREIGN KEY (`pubmed_id`) REFERENCES `pubmed` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `protein2pubmed`
--

LOCK TABLES `protein2pubmed` WRITE;
/*!40000 ALTER TABLE `protein2pubmed` DISABLE KEYS */;
/*!40000 ALTER TABLE `protein2pubmed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provenance`
--

DROP TABLE IF EXISTS `provenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `provenance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_id` int(11) NOT NULL,
  `table_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `column_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `where_clause` text COLLATE utf8_unicode_ci,
  `comment` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `provenance_idx1` (`dataset_id`),
  CONSTRAINT `fk_provenance_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provenance`
--

LOCK TABLES `provenance` WRITE;
/*!40000 ALTER TABLE `provenance` DISABLE KEYS */;
/*!40000 ALTER TABLE `provenance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ptscore`
--

DROP TABLE IF EXISTS `ptscore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ptscore` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `year` int(4) NOT NULL,
  `score` decimal(12,6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ptscore_idx1` (`protein_id`),
  CONSTRAINT `fk_ptscore_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ptscore`
--

LOCK TABLES `ptscore` WRITE;
/*!40000 ALTER TABLE `ptscore` DISABLE KEYS */;
/*!40000 ALTER TABLE `ptscore` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pubmed`
--

DROP TABLE IF EXISTS `pubmed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pubmed` (
  `id` int(11) NOT NULL,
  `title` text COLLATE utf8_unicode_ci NOT NULL,
  `journal` text COLLATE utf8_unicode_ci,
  `date` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `authors` text COLLATE utf8_unicode_ci,
  `abstract` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pubmed`
--

LOCK TABLES `pubmed` WRITE;
/*!40000 ALTER TABLE `pubmed` DISABLE KEYS */;
/*!40000 ALTER TABLE `pubmed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rat_qtl`
--

DROP TABLE IF EXISTS `rat_qtl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rat_qtl` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nhprotein_id` int(11) NOT NULL,
  `rgdid` int(11) NOT NULL,
  `qtl_rgdid` int(11) NOT NULL,
  `qtl_symbol` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `qtl_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `trait_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `measurement_type` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `associated_disease` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `phenotype` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `p_value` decimal(20,19) DEFAULT NULL,
  `lod` float(6,3) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rat_qtl_idx1` (`nhprotein_id`),
  CONSTRAINT `fk_rat_qtl__nhprotein` FOREIGN KEY (`nhprotein_id`) REFERENCES `nhprotein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rat_qtl`
--

LOCK TABLES `rat_qtl` WRITE;
/*!40000 ALTER TABLE `rat_qtl` DISABLE KEYS */;
/*!40000 ALTER TABLE `rat_qtl` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rat_term`
--

DROP TABLE IF EXISTS `rat_term`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rat_term` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rgdid` int(11) NOT NULL,
  `term_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `obj_symbol` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `term_name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `qualifier` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL,
  `evidence` varchar(5) COLLATE utf8_unicode_ci DEFAULT NULL,
  `ontology` varchar(40) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `rat_term_idx1` (`rgdid`,`term_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rat_term`
--

LOCK TABLES `rat_term` WRITE;
/*!40000 ALTER TABLE `rat_term` DISABLE KEYS */;
/*!40000 ALTER TABLE `rat_term` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rdo`
--

DROP TABLE IF EXISTS `rdo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rdo` (
  `doid` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `def` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`doid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rdo`
--

LOCK TABLES `rdo` WRITE;
/*!40000 ALTER TABLE `rdo` DISABLE KEYS */;
/*!40000 ALTER TABLE `rdo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rdo_xref`
--

DROP TABLE IF EXISTS `rdo_xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rdo_xref` (
  `doid` varchar(12) COLLATE utf8_unicode_ci NOT NULL,
  `db` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`doid`,`db`,`value`),
  KEY `rdo_xref__idx2` (`db`,`value`),
  CONSTRAINT `fk_rdo_xref__do` FOREIGN KEY (`doid`) REFERENCES `rdo` (`doid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rdo_xref`
--

LOCK TABLES `rdo_xref` WRITE;
/*!40000 ALTER TABLE `rdo_xref` DISABLE KEYS */;
/*!40000 ALTER TABLE `rdo_xref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t2tc`
--

DROP TABLE IF EXISTS `t2tc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `t2tc` (
  `target_id` int(11) NOT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `nucleic_acid_id` int(11) DEFAULT NULL,
  KEY `t2tc_idx1` (`target_id`),
  KEY `t2tc_idx2` (`protein_id`),
  CONSTRAINT `fk_t2tc__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`),
  CONSTRAINT `fk_t2tc__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t2tc`
--

LOCK TABLES `t2tc` WRITE;
/*!40000 ALTER TABLE `t2tc` DISABLE KEYS */;
/*!40000 ALTER TABLE `t2tc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `target`
--

DROP TABLE IF EXISTS `target`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `target` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `ttype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `comment` text COLLATE utf8_unicode_ci,
  `tdl` enum('Tclin+','Tclin','Tchem+','Tchem','Tbio','Tgray','Tdark') COLLATE utf8_unicode_ci DEFAULT NULL,
  `idg` tinyint(1) NOT NULL DEFAULT '0',
  `fam` enum('Enzyme','Epigenetic','GPCR','IC','Kinase','NR','oGPCR','TF','TF; Epigenetic','Transporter') COLLATE utf8_unicode_ci DEFAULT NULL,
  `famext` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `target`
--

LOCK TABLES `target` WRITE;
/*!40000 ALTER TABLE `target` DISABLE KEYS */;
/*!40000 ALTER TABLE `target` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tdl_info`
--

DROP TABLE IF EXISTS `tdl_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tdl_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `itype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `target_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `nucleic_acid_id` int(11) DEFAULT NULL,
  `string_value` text COLLATE utf8_unicode_ci,
  `number_value` decimal(12,6) DEFAULT NULL,
  `integer_value` int(11) DEFAULT NULL,
  `date_value` date DEFAULT NULL,
  `boolean_value` tinyint(1) DEFAULT NULL,
  `curration_level` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tdl_info_idx1` (`itype`),
  KEY `tdl_info_idx2` (`target_id`),
  KEY `tdl_info_idx3` (`protein_id`),
  CONSTRAINT `fk_tdl_info__info_type` FOREIGN KEY (`itype`) REFERENCES `info_type` (`name`),
  CONSTRAINT `fk_tdl_info__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tdl_info__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tdl_info`
--

LOCK TABLES `tdl_info` WRITE;
/*!40000 ALTER TABLE `tdl_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `tdl_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tdl_update_log`
--

DROP TABLE IF EXISTS `tdl_update_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tdl_update_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) NOT NULL,
  `old_tdl` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `new_tdl` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `person` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `explanation` text COLLATE utf8_unicode_ci,
  `application` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `app_version` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tdl_update_log` (`target_id`),
  CONSTRAINT `fk_tdl_update_log__target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tdl_update_log`
--

LOCK TABLES `tdl_update_log` WRITE;
/*!40000 ALTER TABLE `tdl_update_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `tdl_update_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `techdev_contact`
--

DROP TABLE IF EXISTS `techdev_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `techdev_contact` (
  `id` int(11) NOT NULL,
  `contact_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `contact_email` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `date` date DEFAULT NULL,
  `grant_number` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `pi` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `techdev_contact`
--

LOCK TABLES `techdev_contact` WRITE;
/*!40000 ALTER TABLE `techdev_contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `techdev_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `techdev_info`
--

DROP TABLE IF EXISTS `techdev_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `techdev_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `contact_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `comment` text COLLATE utf8_unicode_ci NOT NULL,
  `publication_pcmid` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `publication_pmid` int(11) DEFAULT NULL,
  `resource_url` text COLLATE utf8_unicode_ci,
  `data_url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `techdev_info_idx1` (`contact_id`),
  KEY `techdev_info_idx2` (`protein_id`),
  CONSTRAINT `fk_techdev_info__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_techdev_info__techdev_contact` FOREIGN KEY (`contact_id`) REFERENCES `techdev_contact` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `techdev_info`
--

LOCK TABLES `techdev_info` WRITE;
/*!40000 ALTER TABLE `techdev_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `techdev_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tinx_articlerank`
--

DROP TABLE IF EXISTS `tinx_articlerank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tinx_articlerank` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `importance_id` int(11) NOT NULL,
  `pmid` int(11) NOT NULL,
  `rank` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tinx_articlerank_idx1` (`importance_id`),
  CONSTRAINT `fk_tinx_articlerank__tinx_importance` FOREIGN KEY (`importance_id`) REFERENCES `tinx_importance` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tinx_articlerank`
--

LOCK TABLES `tinx_articlerank` WRITE;
/*!40000 ALTER TABLE `tinx_articlerank` DISABLE KEYS */;
/*!40000 ALTER TABLE `tinx_articlerank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tinx_disease`
--

DROP TABLE IF EXISTS `tinx_disease`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tinx_disease` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `doid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `summary` text COLLATE utf8_unicode_ci,
  `score` decimal(34,16) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tinx_disease`
--

LOCK TABLES `tinx_disease` WRITE;
/*!40000 ALTER TABLE `tinx_disease` DISABLE KEYS */;
/*!40000 ALTER TABLE `tinx_disease` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tinx_importance`
--

DROP TABLE IF EXISTS `tinx_importance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tinx_importance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `disease_id` int(11) NOT NULL,
  `score` decimal(34,16) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tinx_importance_idx1` (`protein_id`),
  KEY `tinx_importance_idx2` (`disease_id`),
  CONSTRAINT `fk_tinx_importance__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_tinx_importance__tinx_disease` FOREIGN KEY (`disease_id`) REFERENCES `tinx_disease` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tinx_importance`
--

LOCK TABLES `tinx_importance` WRITE;
/*!40000 ALTER TABLE `tinx_importance` DISABLE KEYS */;
/*!40000 ALTER TABLE `tinx_importance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tinx_novelty`
--

DROP TABLE IF EXISTS `tinx_novelty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tinx_novelty` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `protein_id` int(11) NOT NULL,
  `score` decimal(34,16) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tinx_novelty_idx1` (`protein_id`),
  CONSTRAINT `fk_tinx_novelty__protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tinx_novelty`
--

LOCK TABLES `tinx_novelty` WRITE;
/*!40000 ALTER TABLE `tinx_novelty` DISABLE KEYS */;
/*!40000 ALTER TABLE `tinx_novelty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `tinx_target`
--

DROP TABLE IF EXISTS `tinx_target`;
/*!50001 DROP VIEW IF EXISTS `tinx_target`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `tinx_target` AS SELECT 
 1 AS `target_id`,
 1 AS `protein_id`,
 1 AS `uniprot`,
 1 AS `sym`,
 1 AS `tdl`,
 1 AS `fam`,
 1 AS `family`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `uberon`
--

DROP TABLE IF EXISTS `uberon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uberon` (
  `uid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `name` text COLLATE utf8_unicode_ci NOT NULL,
  `def` text COLLATE utf8_unicode_ci,
  `comment` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uberon`
--

LOCK TABLES `uberon` WRITE;
/*!40000 ALTER TABLE `uberon` DISABLE KEYS */;
/*!40000 ALTER TABLE `uberon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uberon_parent`
--

DROP TABLE IF EXISTS `uberon_parent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uberon_parent` (
  `uid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  KEY `uberon_parent_idx1` (`uid`),
  CONSTRAINT `fk_uberon_parent__uberon` FOREIGN KEY (`uid`) REFERENCES `uberon` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uberon_parent`
--

LOCK TABLES `uberon_parent` WRITE;
/*!40000 ALTER TABLE `uberon_parent` DISABLE KEYS */;
/*!40000 ALTER TABLE `uberon_parent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `uberon_xref`
--

DROP TABLE IF EXISTS `uberon_xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `uberon_xref` (
  `uid` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `db` varchar(24) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`uid`,`db`,`value`),
  KEY `uberon_xref_idx1` (`uid`),
  CONSTRAINT `fk_uberon_xref__uberon` FOREIGN KEY (`uid`) REFERENCES `uberon` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `uberon_xref`
--

LOCK TABLES `uberon_xref` WRITE;
/*!40000 ALTER TABLE `uberon_xref` DISABLE KEYS */;
/*!40000 ALTER TABLE `uberon_xref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xref`
--

DROP TABLE IF EXISTS `xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xref` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `xtype` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `target_id` int(11) DEFAULT NULL,
  `protein_id` int(11) DEFAULT NULL,
  `nucleic_acid_id` int(11) DEFAULT NULL,
  `value` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `xtra` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `dataset_id` int(11) NOT NULL,
  `nhprotein_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `xref_idx3` (`xtype`,`target_id`,`value`),
  UNIQUE KEY `xref_idx5` (`xtype`,`protein_id`,`value`),
  KEY `xref_idx1` (`xtype`),
  KEY `xref_idx2` (`target_id`),
  KEY `xref_idx4` (`protein_id`),
  KEY `xref_idx6` (`dataset_id`),
  KEY `fk_xref_nhprotein` (`nhprotein_id`),
  CONSTRAINT `fk_xref__xref_type` FOREIGN KEY (`xtype`) REFERENCES `xref_type` (`name`),
  CONSTRAINT `fk_xref_dataset` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`),
  CONSTRAINT `fk_xref_nhprotein` FOREIGN KEY (`nhprotein_id`) REFERENCES `nhprotein` (`id`),
  CONSTRAINT `fk_xref_protein` FOREIGN KEY (`protein_id`) REFERENCES `protein` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_xref_target` FOREIGN KEY (`target_id`) REFERENCES `target` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xref`
--

LOCK TABLES `xref` WRITE;
/*!40000 ALTER TABLE `xref` DISABLE KEYS */;
/*!40000 ALTER TABLE `xref` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `xref_type`
--

DROP TABLE IF EXISTS `xref_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xref_type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `url` text COLLATE utf8_unicode_ci,
  `eg_q_url` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `xref_type`
--

LOCK TABLES `xref_type` WRITE;
/*!40000 ALTER TABLE `xref_type` DISABLE KEYS */;
INSERT INTO `xref_type` VALUES ('BRENDA',NULL,NULL,NULL),('ChEMBL',NULL,NULL,NULL),('DrugBank',NULL,NULL,NULL),('Ensembl',NULL,NULL,NULL),('ENSG','Ensembl Gene ID',NULL,NULL),('HGNC ID',NULL,NULL,NULL),('InterPro',NULL,NULL,NULL),('L1000 ID','CMap landmark gene ID. See http://support.lincscloud.org/hc/en-us/articles/202092616-The-Landmark-Genes',NULL,NULL),('MGI ID',NULL,NULL,NULL),('MIM',NULL,NULL,NULL),('NCBI GI',NULL,NULL,NULL),('PANTHER',NULL,NULL,NULL),('PDB',NULL,NULL,NULL),('Pfam',NULL,NULL,NULL),('PROSITE',NULL,NULL,NULL),('PubMed',NULL,NULL,NULL),('RefSeq','RefSeq mappings loaded from UniProt XML',NULL,NULL),('SMART',NULL,NULL,NULL),('STRING','STRING ENSP mappings loaded from UniProt XML',NULL,NULL),('UniGene',NULL,NULL,NULL),('UniProt Keyword','UniProt keyword ids and values',NULL,NULL);
/*!40000 ALTER TABLE `xref_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `tinx_target`
--

/*!50001 DROP VIEW IF EXISTS `tinx_target`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`smathias`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `tinx_target` AS select `t`.`id` AS `target_id`,`p`.`id` AS `protein_id`,`p`.`uniprot` AS `uniprot`,`p`.`sym` AS `sym`,`t`.`tdl` AS `tdl`,`t`.`fam` AS `fam`,`p`.`family` AS `family` from ((`target` `t` join `t2tc`) join `protein` `p`) where ((`t`.`id` = `t2tc`.`target_id`) and (`t2tc`.`protein_id` = `p`.`id`) and `p`.`id` in (select distinct `tinx_novelty`.`protein_id` from `tinx_novelty`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-05-04 11:06:26
