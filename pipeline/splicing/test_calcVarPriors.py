import unittest
import mock
import calcVarPriors
from calcVarPriors import STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH
from calcVarPriors import STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, STD_DE_NOVO_OFFSET, BRCA1_RefSeq, BRCA2_RefSeq
import calcMaxEntScanMeanStd
from calcVarPriorsMockedResponses import brca1Exons, brca2Exons 
from calcVarPriorsMockedResponses import brca1RefSpliceDonorBounds, brca2RefSpliceDonorBounds 
from calcVarPriorsMockedResponses import brca1RefSpliceAcceptorBounds, brca2RefSpliceAcceptorBounds
from calcVarPriorsMockedResponses import variantData

# fill in argument for genome
GENOME = "hg38"

# dictionary containing possible strands for variants
strand = {"minus": "-",
          "plus": "+"}

# dictionary containing possible chromosomes for variants
chromosomes = {"13": "chr13",
               "17": "chr17"}

# dictionary containing possible variant types
varTypes = {"sub": "substitution",
            "ins": "insertion",
            "del": "deletion",
            "delins": "delins"}

# dictionary containing the number of exons for particular genes
numExons = {"BRCA1": 23,
            "BRCA2": 27}

# example donor exon boundaries for BRCA1 and BRCA2
exonDonorBoundsBRCA1 = {"exon16": {"donorStart": 43070930,
                                   "donorEnd": 43070922}}
exonDonorBoundsBRCA2 = {"exon15": {"donorStart": 32356607,
                                   "donorEnd": 32356615}}

# example acceptor exon boundaries for BRCA1 and BRCA2
exonAcceptorBoundsBRCA1 = {"exon21": {"acceptorStart": 43051137,
                                      "acceptorEnd": 43051115}}
exonAcceptorBoundsBRCA2 = {"exon20": {"acceptorStart": 32370936,
                                      "acceptorEnd": 32370958}}

# dictionary containing possible variant locations
variantLocations = {"outBounds": "outside_transcript_boundaries_variant",
                    "inCI": "CI_domain_variant",
                    "inCISpliceDonor": "CI_splice_donor_variant",
                    "inCISpliceAcceptor": "CI_splice_acceptor_variant",
                    "inSpliceDonor": "splice_donor_variant",
                    "inSpliceAcceptor": "splice_acceptor_variant",
                    "inGreyZone": "grey_zone_variant",
                    "afterGreyZone": "after_grey_zone_variant",
                    "inExon": "exon_variant",
                    "inUTR": "UTR_variant",
                    "inIntron": "intron_variant"}

# transcript data to mock response from fetch_gene_coordinates for BRCA1 and BRCA2
transcriptDataBRCA1 = {'bin': '114',
                       'exonEnds': '43045802,43047703,43049194,43051117,43057135,43063373,43063951,43067695,43071238,43074521,43076614,43082575,43091032,43094860,43095922,43097289,43099880,43104261,43104956,43106533,43115779,43124115,43125483,',
                       'exonFrames': '1,0,1,0,0,1,1,0,1,2,1,0,1,1,2,1,0,1,2,2,2,0,-1,',
                       'name': 'NM_007294.3',
                       'txStart': 43044294,
                       'exonCount': 23,
                       'cdsEndStat': 'cmpl',
                       'cdsEnd': 43124096,
                       'score': 0,
                       'name2': 'BRCA1',
                       'strand': '-',
                       'cdsStart': 43045677,
                       'cdsStartStat': 'cmpl',
                       'chrom': 'chr17',
                       'txEnd': 43125483,
                       'exonStarts': '43044294,43047642,43049120,43051062,43057051,43063332,43063873,43067607,43070927,43074330,43076487,43082403,43090943,43091434,43095845,43097243,43099774,43104121,43104867,43106455,43115725,43124016,43125270,'}

transcriptDataBRCA2 = {'bin': '103',
                       'exonEnds': '32315667,32316527,32319325,32325184,32326150,32326282,32326613,32329492,32331030,32333387,32341196,32344653,32346896,32355288,32356609,32357929,32362693,32363533,32370557,32371100,32376791,32379515,32379913,32380145,32394933,32397044,32399672,',
                       'exonFrames': '-1,0,1,1,2,1,0,1,0,1,1,1,1,2,1,0,2,2,0,0,1,0,1,0,1,0,0,',
                       'name': 'NM_000059.3',
                       'txStart': 32315479,
                       'exonCount': 27,
                       'cdsEndStat': 'cmpl',
                       'cdsEnd': 32398770,
                       'score': 0,
                       'name2': 'BRCA2',
                       'strand': '+',
                       'cdsStart': 32316460,
                       'cdsStartStat': 'cmpl',
                       'chrom': 'chr13',
                       'txEnd': 32399672,
                       'exonStarts': '32315479,32316421,32319076,32325075,32326100,32326241,32326498,32329442,32330918,32332271,32336264,32344557,32346826,32354860,32356427,32357741,32362522,32363178,32370401,32370955,32376669,32379316,32379749,32380006,32394688,32396897,32398161,'}

# sample sequence data for BRCA1 and BRCA2
brca1Seq = "GATCTGGAAGAAGAGAGGAAGAG"
brca2Seq = "TGTGTAACACATTATTACAGTGG"

# MaxEntScan score mean and std for donors and acceptors
meanStdDict =  {"donors": {"std": 2.3289956850167082,
                           "mean": 7.9380909090909073},
                "acceptors": {"std": 2.4336623152078452,
                              "mean": 7.984909090909091}}

# possible predicted qualitative ENIGMA classes
enigmaClasses = {"class1": "class_1",
                 "class2": "class_2",
                 "class3": "class_3",
                 "class4": "class_4",
                 "class5": "class_5",
                 "NA": "N/A"}

# possible prior probability of pathogenecity values
priorProbs = {"deNovoLow": 0.02,
              "proteinLow": 0.03,
              "low": 0.04,
              "proteinMod": 0.29,
              "deNovoMod": 0.3,
              "moderate": 0.34,
              "capped": 0.5,
              "deNovoHigh": 0.64,
              "proteinHigh": 0.81,
              "high": 0.97,
              "pathogenic": 0.99,
              "NA": "N/A"}


class test_calcVarPriors(unittest.TestCase):

    def setUp(self):

        self.variant = {"Chr": "13",
                        "Pos": "32314943",
                        "Ref": "A",
                        "Alt": "G",
                        "Gene_Symbol": "BRCA2",
                        "Reference_Sequence": "NM_000059.3",
                        "HGVS_cDNA": "c.-764A>G"}
                  
    def test_checkSequence(self):
        '''Tests that checkSequence function categorized acceptable sequences correctly'''
        # sequence with unacceptable letters
        self.variant["Ref"] = "ATGSFHG"
        self.variant["Alt"] = "AGTHA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with numbers
        self.variant["Ref"] = "3452345"
        self.variant["Alt"] = "3456324"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # blank sequence
        self.variant["Ref"] = ""
        self.variant["Alt"] = ""
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertFalse(acceptableRefSeq)
        self.assertFalse(acceptableAltSeq)

        # sequence with only ATCG
        self.variant["Ref"] = "ATGACG"
        self.variant["Alt"] = "AGTAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)

        # sequence containing all possible acceptable bases
        self.variant["Ref"] = "ATGRACYGN"
        self.variant["Alt"] = "YAGRTNAATA"
        acceptableRefSeq = calcVarPriors.checkSequence(self.variant["Ref"])
        acceptableAltSeq = calcVarPriors.checkSequence(self.variant["Alt"])
        self.assertTrue(acceptableRefSeq)
        self.assertTrue(acceptableAltSeq)

    def test_getVarStrand(self):
        '''Tests that variant strand is set correctly based on variant's gene_symbol'''
        self.variant["Gene_Symbol"] = "BRCA1"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, strand["minus"])

        self.variant["Gene_Symbol"] = "BRCA2"
        varStrand = calcVarPriors.getVarStrand(self.variant)
        self.assertEquals(varStrand, strand["plus"])

    def test_getVarChrom(self):
        '''Tests taht variant chromosome is set correctly based on variant's gene_symbol'''
        self.variant["Gene_Symbol"] = "BRCA1"
        varChrom = calcVarPriors.getVarChrom(self.variant)
        self.assertEquals(varChrom, chromosomes["17"])

        self.variant["Gene_Symbol"] = "BRCA2"
        varChrom = calcVarPriors.getVarChrom(self.variant)
        self.assertEquals(varChrom, chromosomes["13"])

    @mock.patch('calcVarPriors.checkSequence', return_value = True)
    def test_getVarType(self, checkSequence):
        '''
        Tests that variant type is set correctly to substitution, deletion, insertion, or delins based on variant "Ref" and "Alt" values
        '''
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["sub"])

        self.variant["Ref"] = "A"
        self.variant["Alt"] = "AAA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["ins"])

        self.variant["Ref"] = "AGT"
        self.variant["Alt"] = "A"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["del"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "AGTA"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "AGTA"
        self.variant["Alt"] = "AG"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "AG"
        self.variant["Alt"] = "GT"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "A"
        self.variant["Alt"] = "GCTCT"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

        self.variant["Ref"] = "CC"
        self.variant["Alt"] = "G"
        varType = calcVarPriors.getVarType(self.variant)
        self.assertEquals(varType, varTypes["delins"])

    def test_getVarConsequences(self):
        '''
        Tests that:
        1. Variants with non-BRCA1/BRCA2 chromosomes are skipped
        2. Variants with Alt alleles that are not one of the 4 canonical bases are skipped
        '''

        self.variant["Chr"] = ""
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "41160094"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "chr17:g.43008077:TAGG"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32339320"
        self.variant["Hg38_End"] = "32339320"
        self.variant["Alt"] = "R"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "-"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

        self.variant["Alt"] = "38413620"
        varCons = calcVarPriors.getVarConsequences(self.variant)
        self.assertEquals(varCons, "unable_to_determine")

    def test_checkWithinBoundaries(self):
        '''
        Tests that positions are correctly identified as in/not in boundaries and that boundaries are inclusive
        '''
        varStrand = strand["plus"]
        boundaryStart = 32357742
        boundaryEnd = 32357780

        # check that last position before boundary start is NOT included
        position = 32357741
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that first position after boundary end is NOT included
        position = 32357781
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that boundaryStart is included
        position = 32357742
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that boundaryEnd is included
        position = 32357780
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that position within boundaries is included
        position = 32357758
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        varStrand = strand["minus"]
        boundaryStart = 43067695
        boundaryEnd = 43067649

        # check that last position before boundary start is NOT included
        position = 43067696
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that first position after boundary end is NOT included
        position = 43067648
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertFalse(withinBoundaries)

        # check that boundaryStart is included
        position = 43067695
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)
        
        # check that boundaryEnd is included
        position = 43067649
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)

        # check that position within boundaries is included
        position = 43067669
        withinBoundaries = calcVarPriors.checkWithinBoundaries(varStrand, position, boundaryStart, boundaryEnd)
        self.assertTrue(withinBoundaries)        

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varOutsideBoundariesSNSInsertionBRCA1(self, getVarStrand):
        # SNS and insertion variants all have the same value for Pos, Hg38_Start, and Hg38_End
        '''Tests that SNS/insertion variant outside/inside transcript boundaries are correctly identified for BRCA1'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for BRCA1 SNS/insertion variant outside transcript boundaries
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43044274"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA1 SNS/insertion variant inside transcript boundaries
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43076580"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varOutsideBoundariesDeletionDelinsBRCA1(self, getVarStrand):
        '''Tests that deletion/delins variant outside/inside transcript boundaries are correctly identified for BRCA1'''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for BRCA1 deletion/delins variant outside transcript boundaries
        self.variant["Pos"] = "43041562"
        self.variant["Hg38_Start"] = "43041562"
        self.variant["Hg38_End"] = "43041567"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA1 deletion/delins variant inside transcript boundaries
        self.variant["Pos"] = "43037404"
        self.variant["Hg38_Start"] = "43037404"
        self.variant["Hg38_End"] = "43048457"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varOutsideBoundariesSNSInsertionBRCA2(self, getVarStrand):
        '''Tests that SNS/insertion variant outside/inside transcript boundaries are correctly identified for BRCA2'''
        # SNS and insertion variants all have the same value for Pos, Hg38_Start, and Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for BRCA2 SNS/insertion variant outside transcript boundaries
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32315326"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA2 SNS/insertion variant inside transcript boundaries
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326500"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varOutsideBoundariesDeletionDelinsBRCA2(self, getVarStrand):
        '''Tests that deletion/delins variant outside/inside transcript boundaries are correctly identified for BRCA2'''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for BRCA2 deletion variant outside transcript boundaries
        self.variant["Pos"] = "32315225"
        self.variant["Hg38_Start"] = "32315225"
        self.variant["Hg38_End"] = "32315228"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertTrue(varOutBounds)

        # checks for BRCA2 deletion variant inside transcript boundaries
        self.variant["Pos"] = "32326575"
        self.variant["Hg38_Start"] = "32326575"
        self.variant["Hg38_End"] = "32326578"
        varOutBounds = calcVarPriors.varOutsideBoundaries(self.variant)
        self.assertFalse(varOutBounds)        
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInUTRSNSInsertionBRCA1(self, varOutsideBoundaries, getVarStrand):
        '''Tests that SNS/insertion variants in 5' and 3' UTR are correctly identified for BRCA1'''
        # SNS and insertion variants all have the same value for Pos, Hg38_Start, and Hg38_End
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks for BRCA1 SNS/insertion variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124110"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA1 SNS/insertion variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43044859"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA1 SNS/insertion variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43049184"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA1 SNS/insertion variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43109041"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInUTRDeletionDelinsBRCA1(self, varOutsideBoundaries, getVarStrand):
        '''Tests that deletion/delins variants in 5' and 3' UTR are correctly identified for BRCA1'''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks for BRCA1 deletion/delins variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124128"
        self.variant["Hg38_End"] = "43124132"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA1 deletion/delins variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43044822"
        self.variant["Hg38_End"] = "43044824"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA1 deletion/delins variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43094325"
        self.variant["Hg38_End"] = "43094331"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA1 deletion/delins variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43063317"
        self.variant["Hg38_End"] = "43063330"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA1 deletion/delins variant that crosses boundary between UTR and other region
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43037404"
        self.variant["Hg38_End"] = "43048457"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA1 deletion/delins variant that does NOT cross boundary between UTR and other region
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43044823"
        self.variant["Hg38_End"] = "43044824"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInUTRSNSInsertionBRCA2(self, varOutsideBoundaries, getVarStrand):
        '''Tests that SNS/insertion variants in 5' and 3' UTR are correctly identified for BRCA2'''
        # SNS and insertion variants all have the same value for Pos, Hg38_Start, and Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks for BRCA2 SNS/insertion variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32315497"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA2 SNS/insertion variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398781"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA2 SNS/insertion variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326146"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA2 SNS/insertion variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32396875"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInUTRDeletionDelinsBRCA2(self, varOutsideBoundaries, getVarStrand):
        '''Tests that deletion/delins variants in 5' and 3' UTR are correctly identified for BRCA2'''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks for BRCA2 deletion/delins variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32315664"
        self.variant["Hg38_End"] = "32315666"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)
        
        # checks for BRCA2 deletion/delins variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398787"
        self.variant["Hg38_End"] = "32398790"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA2 deletion/delins variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32336799"
        self.variant["Hg38_End"] = "32336800"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA2 deletion/delins variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32325206"
        self.variant["Hg38_End"] = "32325242"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertFalse(varInUTR)

        # checks for BRCA2 deletion/delins variant that crosses boundary between UTR and other region
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316453"
        self.variant["Hg38_End"] = "32316469"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

        # checks for BRCA2 deletion/delins variant that does NOT cross boundary between UTR and other region
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316435"
        self.variant["Hg38_End"] = "32316436"
        varInUTR = calcVarPriors.varInUTR(self.variant)
        self.assertTrue(varInUTR)

    def test_getExonBoundariesBRCA1(self):
        '''
        Tests that:
        1. Exon boundaries are set correctly for gene on minus strand (BRCA1)
            - checks that exon does not start before it ends
            - next exon does not start before current exon ends
        2. length of varExons matches number of exons for BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        varExons = calcVarPriors.getExonBoundaries(self.variant)
        # check correct number of exons
        self.assertEquals(len(varExons), numExons["BRCA1"])
        # because '-' strand gene, checks that exonStart > exonEnd
        for exon in varExons.keys():
            exonBounds = varExons[exon]
            self.assertGreater(exonBounds["exonStart"], exonBounds["exonEnd"])
            currentExonNum = int(exon[4:])
            nextExonNum = str(currentExonNum + 1)
            nextExonKey = "exon" + nextExonNum
            if nextExonNum <= numExons["BRCA1"]:
                nextExonStart = varExons[nextExonKey]["exonStart"]
                # checks that next exon does not start before current exon ends
                self.assertGreater(exonBounds["exonEnd"], nextExonStart)

    def test_getExonBoundariesBRCA2(self):
        '''
        Tests that:
        1. Exon boundaries are set correctly for gene on plus strand (BRCA2)
            - checks that exon does not start before it ends
            - next exon does not start before current exon ends
        2. length of varExons matches number of exons for BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        varExons = calcVarPriors.getExonBoundaries(self.variant)
        # check correct number of exons
        self.assertEquals(len(varExons), numExons["BRCA2"])
        # because '+' strand gene, checks that exonEnd > exonStart
        for exon in varExons.keys():
            exonBounds = varExons[exon]
            self.assertGreater(exonBounds["exonEnd"], exonBounds["exonStart"])
            currentExonNum = int(exon[4:])
            nextExonNum = str(currentExonNum + 1)
            nextExonKey = "exon" + nextExonNum
            if nextExonNum <= numExons["BRCA2"]:
                nextExonStart = varExons[nextExonKey]["exonStart"]
                # checks that next exon does not start before current exon ends
                self.assertGreater(nextExonStart, exonBounds["exonEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefSpliceDonorBoundariesBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that splice donor boundaries are set correctly for reference transcript (NM_000059.3) and strand (-)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        spliceDonorBounds = calcVarPriors.getRefSpliceDonorBoundaries(self.variant, STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH)
        # checks that region after last exon is not considered a splice donor region
        self.assertNotIn("exon24", spliceDonorBounds)
        # to find exon specified in global variables
        exon = exonDonorBoundsBRCA1.keys()[0]
        self.assertEquals(exonDonorBoundsBRCA1[exon]["donorStart"],
                          spliceDonorBounds[exon]["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA1[exon]["donorEnd"],
                          spliceDonorBounds[exon]["donorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefSpliceDonorBoundariesBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that splice donor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        spliceDonorBounds = calcVarPriors.getRefSpliceDonorBoundaries(self.variant, STD_DONOR_INTRONIC_LENGTH, STD_DONOR_EXONIC_LENGTH)
        # checks that region after last exon is not considered a splice donor region
        self.assertNotIn("exon27", spliceDonorBounds)
        # to find exon specified in global variables
        exon = exonDonorBoundsBRCA2.keys()[0]
        self.assertEquals(exonDonorBoundsBRCA2[exon]["donorStart"],
                          spliceDonorBounds[exon]["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA2[exon]["donorEnd"],
                          spliceDonorBounds[exon]["donorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getSpliceAcceptorBoundariesRefBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that ref splice acceptor boundaries are set correctly for reference transcript (NM_007294.3) and strand (-)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        spliceAcceptorBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH)
        # checks that region before first exon is not considered a splice acceptor region
        self.assertNotIn("exon1", spliceAcceptorBounds)
        # to find exon specified in global variables
        exon = exonAcceptorBoundsBRCA1.keys()[0]
        self.assertEquals(exonAcceptorBoundsBRCA1[exon]["acceptorStart"],
                          spliceAcceptorBounds[exon]["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA1[exon]["acceptorEnd"],
                          spliceAcceptorBounds[exon]["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getSpliceAcceptorBoundariesDeNovoBRCA1(self, getExonBoundaries, getVarStrand):
        '''
        Tests that de novo splice acceptor boundaries are set correctly for reference transcript (NM_007294.3) and strand (-)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        deNovoSpliceAccBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_DE_NOVO_LENGTH)
        expectedDeNovoRegionExon6 = {"acceptorStart": 43104976,
                                     "acceptorEnd": 43104947}
        self.assertEquals(deNovoSpliceAccBounds["exon6"]["acceptorStart"],
                          expectedDeNovoRegionExon6["acceptorStart"])
        self.assertEquals(deNovoSpliceAccBounds["exon6"]["acceptorEnd"],
                          expectedDeNovoRegionExon6["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getSpliceAcceptorBoundariesRefBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that ref splice acceptor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        Uses example boundaries defined at beginning of script
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        spliceAcceptorBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_ACC_EXONIC_LENGTH)
        # checks that region before first exon is not considered a splice acceptor region
        self.assertNotIn("exon1", spliceAcceptorBounds)
        # to find exon specified in global variables
        exon = exonAcceptorBoundsBRCA2.keys()[0]
        self.assertEquals(exonAcceptorBoundsBRCA2[exon]["acceptorStart"],
                          spliceAcceptorBounds[exon]["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA2[exon]["acceptorEnd"],
                          spliceAcceptorBounds[exon]["acceptorEnd"])

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getSpliceAcceptorBoundariesDeNovoBRCA2(self, getExonBoundaries, getVarStrand):
        '''
        Tests that de novo splice acceptor boundaries are set correctly for reference transcript (NM_000059.3) and strand (+)
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        deNovoSpliceAccBounds = calcVarPriors.getSpliceAcceptorBoundaries(self.variant, STD_ACC_INTRONIC_LENGTH, STD_DE_NOVO_LENGTH)
        expectedDeNovoRegionExon8 = {"acceptorStart": 32329423,
                                     "acceptorEnd": 32329452}
        self.assertEquals(deNovoSpliceAccBounds["exon8"]["acceptorStart"],
                          expectedDeNovoRegionExon8["acceptorStart"])
        self.assertEquals(deNovoSpliceAccBounds["exon8"]["acceptorEnd"],
                          expectedDeNovoRegionExon8["acceptorEnd"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInExonBRCA1(self, varOutsideBoundaries, getExonBoundaries, getVarStrand):
        '''Tests that variant is correctly identified as inside or outside an exon for BRCA1'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks BRCA1 SNS/insertion variant at 5' exon boundary (last base in intron)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104957"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA1 SNS/insertion variant at 5' exon boundary (first base in exon)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104956"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 SNS/insertion variant 3' exon boundary (last base in exon)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43067608"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 SNS/insertion variant 3' exon boundary (first base in intron)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43067607"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)
        
        # checks BRCA1 SNS/insertion variant inside an exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43049176"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 SNS/insertion variant outside an exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045827"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA1 deletion/delins variant that crosses exon boundary
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43045963"
        self.variant["Hg38_End"] = "43048457"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 deletion/delins variant that is entirely inside exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43070967"
        self.variant["Hg38_End"] = "43070969"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA1 deletion/delins variant that is entirely outside exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43106544"
        self.variant["Hg38_End"] = "43106548"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA1 deletion/delins variant that is just outside exon (-1)
        self.variant["HGVS_cDNA"] = "c.81-5_81-1delinsACCTTGA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43115780"
        self.variant["Hg38_End"] = "43115784"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA1 deletion/delins variant that is just outside exon (+1)
        self.variant["HGVS_cDNA"] = "c.212+1delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43106454"
        self.variant["Hg38_End"] = "43106455"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA1 deletion/delins variant that is just inside exon (starts at first base)
        self.variant["HGVS_cDNA"] = "c.548delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43097288"
        self.variant["Hg38_End"] = "43097289"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks for BRCA1 deletion/delins variant is is just insde exon (ends as last base)
        # this is a fictional variant
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43097243"
        self.variant["Hg38_End"] = "43097244"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInExonBRCA2(self, varOutsideBoundaries, getExonBoundaries, getVarStrand):
        '''Tests that variant is correctly identified as inside or outside an exon for BRCA2'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks BRCA2 SNS/insertion variant at 5' exon boundary (last base in intron)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32357741"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA2 SNS/insertion variant at 5' exon boundary (first base in exon)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32357742"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 SNS/insertion variant at 3' exon boundary (last base in exon)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32370557"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 SNS/insertion variant at 3' exon boundary (first base in intron)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32370558"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)
        
        # checks BRCA2 SNS/insertion variant inside an exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398201"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # cehcks BRCA2 SNS/insertion variant outside an exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32396873"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks BRCA2 deletion/delins variant that crosses exon boundary
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379749"
        self.variant["Hg38_End"] = "32379751"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 deletion/delins variant that is entirely inside exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32357802"
        self.variant["Hg38_End"] = "32357804"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks BRCA2 deletion/delins variant that is entirely outside exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32363176"
        self.variant["Hg38_End"] = "32363177"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA2 deletion/delins variant that is just outside exon (-1)
        self.variant["HGVS_cDNA"] = "c.476-4_476-1delCCAGinsT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32326238"
        self.variant["Hg38_End"] = "32326241"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA2 deletion/delins variant that is just outside exon (+1)
        self.variant["HGVS_cDNA"] = "c.8953+1delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379515"
        self.variant["Hg38_End"] = "32379516"
        self.variant["Ref"] = "GG"
        self.variant["Alt"] = "G"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertFalse(inExon)

        # checks for BRCA2 deletion/delins variant that is just inside exon (starts at first base)
        # this variant does not exist in database as of 5/11/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32329442"
        self.variant["Hg38_End"] = "32329443"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

        # checks for BRCA2 deletion/delins variant is is just insde exon (ends as last base)
        # this variant does not exist in database as of 5/11/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32329491"
        self.variant["Hg38_End"] = "32329492"
        inExon = calcVarPriors.varInExon(self.variant)
        self.assertTrue(inExon)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getVarExonNumberSNSBRCA1(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is set correctly for minus strand (BRCA1) variant in exon'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # variant position in exon 13
        self.variant["Pos"] = "43082564"
        print self.variant
        varExonNum = calcVarPriors.getVarExonNumberSNS(self.variant)
        self.assertEquals(varExonNum, "exon13")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getVarExonNumberSNSBRCA2(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is set correctly for plus strand (BRCA2) variant in exon'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # variant position in exon 4
        self.variant["Pos"] = "32325166"
        varExonNum = calcVarPriors.getVarExonNumberSNS(self.variant)
        self.assertEquals(varExonNum, "exon4")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getVarExonNumberStructuralVarDeletionBRCA1(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for minus strand (BRCA1) deletion variants'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for BRCA1 deletion variant that spans multiple exons
        # this variant spans exons 20-22
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43048588"
        self.variant["Hg38_End"] = "43059975"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon20", "exon21", "exon22"])

        # checks for BRCA1 deletion variant that is contained in a single exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43051062"
        self.variant["Hg38_End"] = "43051116"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon21"])

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getVarExonNumberStructuralVarDeletionBRCA2(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for plus strand (BRCA2) deletion variants'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for BRCA2 deletion variant that spans multiple exons
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32340772"
        self.variant["Hg38_End"] = "32355272"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon11", "exon12", "exon13", "exon14"])

        # checks for BRCA2 deletion variant that is contained in a single exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32317677"
        self.variant["Hg38_End"] = "32321583"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon3"])

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getVarExonNumberStructuralVarInsertionBRCA1(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for minus strand (BRCA1) insertion variants'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for large BRCA1 insertion variant
        self.variant["HGVS_cDNA"] = "c.442-952_547dup"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43099774"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon8"])

        # checks for small BRCA1 insertion variant
        self.variant["HGVS_cDNA"] = "c.4107_4108insATCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43091021"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon12"])

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getVarExonNumberStructuralVarInsertionBRCA2(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for plus strand (BRCA2) deletion variants'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for large BRCA2 insertion variant
        self.variant["HGVS_cDNA"] = "c.9517_9518insTCTAAGTCAAATGTTTTCAAAACAATTGACATTGTTTTCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32396912"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon26"])

        # checks for small BRCA2 insertion variant
        self.variant["HGVS_cDNA"] = "c.2175dupA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32336524"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon11"])

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getVarExonNumberStructuralVarDelinsBRCA1(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for minus strand (BRCA1) delins variants'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"

        # checks for large BRCA1 delins variant
        self.variant["HGVS_cDNA"] = "c.5468-285_*4019delinsCACAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43041662"
        self.variant["Hg38_End"] = "43046087"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon24"])

        # checks for small BRCA1 delins variant
        self.variant["HGVS_cDNA"] = "c.5331_5332+1delAGGinsCAACAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43051062"
        self.variant["Hg38_End"] = "43051064"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon21"])

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getVarExonNumberStructuralVarDelinsBRCA2(self, varInExon, getVarType, getExonBoundaries, getVarStrand):
        '''Tests that exon number is correctly identified for plus strand (BRCA2) delins variants'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"

        # checks for large BRCA2 delins variant
        self.variant["HGVS_cDNA"] = "c.5550_5566delAATCGTTTGTGTTTCACinsTTGGCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32339905"
        self.variant["Hg38_End"] = "32339921"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon11"])

        # checks for small BRCA2 delins variant
        self.variant["HGVS_cDNA"] = "c.593_596delTAGCinsAGG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32326575"
        self.variant["Hg38_End"] = "32326578"
        varExonNum = calcVarPriors.getVarExonNumberStructuralVar(self.variant)
        self.assertItemsEqual(varExonNum, ["exon7"])
        
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionDonorBRCA1SNSRef(self, getRefDonorBoundaries, getVarType):
        '''
        Tests that:
        1. SNS variant is correctly identified as in or NOT in a splice donor region 
           for multiple positions across multiple exons in BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = False

        #checks that 7th base in intron is NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43063326"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)
        
        # checks that first base in intron counted as in splice donor
        self.variant["Pos"] =  self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43097243"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in intron counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43095842"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in intron counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43091429"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that first base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43090946"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43082405"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43076488"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that 4th to last base in exon is NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43057055"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that region after exon 24 is  NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43044294"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionDonorBRCA1DeNovoTrue(self, getExonBoundaries, varInExon, getVarType):
        '''Tests that function correctly identifies if variant is IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = True

        # checks that variant in an exon is marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104232"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

        # checks that variant in intronic portion of reference splice donor is marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104117"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionDonorBRCA1SNSDeNovoFalse(self, getExonBoundaries, varInExon, getVarType):
        '''Tests that function correctly identifies if SNS variant is NOT IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104101"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

        # checks that last variant in an intron (-1) is NOT marked as being in a de novo donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106534"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

        # checks that 1st base after ref splice donor region (+7) is NOT marked as being in a de novo donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106449"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    def test_varInSpliceRegionDonorBRCA1DeletionDelins(self, getRefSpliceDonorBoundaries, getVarStrand,
                                                       getVarType, getExonBoundaries):
        '''
        Tests that funciton correctly identifies deletion/delins variants as in/NOT in 
           ref and de novo splice regions for minus strand gene (BRCA1)
        '''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks that deletion/delins variant entirely in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.134+2delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43115723"
        self.variant["Hg38_End"] = "43115724"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant partially in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.190_211delTGTAAGAATGATATAACCAAAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43106456"
        self.variant["Hg38_End"] = "43106478"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)
        
        # checks that deletion/delins variant entirely NOT in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5450_5451delAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43047658"
        self.variant["Hg38_End"] = "43047660"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that deletion/delins variant entirely in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.239_241delGTCinsTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104928"
        self.variant["Hg38_End"] = "43104930"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)
    
        # checks that deletion/delins variant partially in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.208_212+22del27"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43106433"
        self.variant["Hg38_End"] = "43106460"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant entirely NOT in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.302-2_302-1del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104261"
        self.variant["Hg38_End"] = "43104263"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertFalse(inSpliceRegion)
        
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInSpliceRegionDonorBRCA1Insertion(self, getRefSpliceDonorBoundaries, getVarStrand,
                                                  getExonBoundaries, getVarType):
        '''
        Tests that funciton correctly identifies insertion variants as in/NOT in 
           ref and de novo splice regions for minus strand gene (BRCA1)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks that insertion variant in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5152+3_5152+4insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43063869"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that insertion variant NOT in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.190_191insAATGTAAGGATGATATAAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106477"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that insertion variant in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.4163dupA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43090966"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)
        
        # checks that insertion variatn NOT in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.4185+21_4185+22dupTG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43090921"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertFalse(inSpliceRegion)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    def test_getVarSpliceRegionBoundsDonorBRCA1SNS(self, varInSpliceRegion, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given SNS variant (genomic position)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = True
        deNovo = False
    
        # checks that variant in exon 16 splice donor region boundaries are returned correctly
        self.variant["Pos"] = "43070925"
        spliceDonorRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceDonorRegion["exonName"], "exon16")
        self.assertEquals(exonDonorBoundsBRCA1["exon16"]["donorStart"], spliceDonorRegion["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA1["exon16"]["donorEnd"], spliceDonorRegion["donorEnd"])
        
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    def test_varInSpliceRegionDonorBRCA2SNSRef(self, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. SNS variant is correctly identified as in or NOT in a splice donor region 
           for multiple positions across multiple exons in BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = False

        # checks that 7th base in intron is NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32363540"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that first base in intron counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32329493"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in intron counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32331033"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in intron counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32333393"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that first base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32341194"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that middle base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32344652"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that last base in exon counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32346896"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceDonor)

        # checks that 4th to last base in exon is NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32370554"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

        # checks that region after  exon 27 is NOT counted as in splice donor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32399672"
        inSpliceDonor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceDonor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', reutrn_value = varTypes["sub"])
    def test_varInSpliceRegionDonorBRCA2SNSDeNovoTrue(self, getExonBoundaries, varInExon, getVarType):
        '''Tests that function correctly identifies if SNS variant is IN a de novo splice region for plus strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = True

        # checks that variant in an exon is marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379784"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

        # checks that variant in intronic portion of reference splice donor is marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379914"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionDonorBRCA2SNSDeNovoFalse(self, getExonBoundaries, varInExon, getVarType):
        '''Tests that function correctly identifies if SNS variant is NOT IN a de novo splice region for pluis strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379743"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

        # checks that last variant in an intron (-1) is NOT marked as being in a de novo donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32356427"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

        # checks that 1st base after ref splice donor region (+7) is NOT marked as being in a de novo donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32356616"
        inDeNovoDonorRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoDonorRegion)

    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    def test_varInSpliceRegionDonorBRCA2DeletionDelins(self, getRefSpliceDonorBoundaries, getVarStrand,
                                                       getVarType, getExonBoundaries):
        '''
        Tests that funciton correctly identifies deletion/delins variants as in/NOT in 
           ref and de novo splice regions for plus strand gene (BRCA2)
        '''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks that deletion/delins variant entirely in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.316+4delA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32319328"
        self.variant["Hg38_End"] = "32319329"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant partially in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.1905_1909delTTCAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32333382"
        self.variant["Hg38_End"] = "32333387"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)
        
        # checks that deletion/delins variant entirely NOT in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.6841+7_6841+8delGT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32341202"
        self.variant["Hg38_End"] = "32341204"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that deletion/delins variant entirely in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.765_770delCACAAAinsAAACAAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32331002"
        self.variant["Hg38_End"] = "32331007"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)
    
        # checks that deletion/delins variant partially in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.8954-1_8955delGTTinsAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379749"
        self.variant["Hg38_End"] = "32379751"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant entirely NOT in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.8488-20_8488-17del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32370932"
        self.variant["Hg38_End"] = "32370936"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertFalse(inSpliceRegion)
        
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInSpliceRegionDonorBRCA2Insertion(self, getRefSpliceDonorBoundaries, getVarStrand,
                                                  getExonBoundaries, getVarType):
        '''
        Tests that funciton correctly identifies insertion variants as in/NOT in 
           ref and de novo splice regions for plus strand gene (BRCA2)
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks that insertion variant in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.681+2dupT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32329494"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that insertion variant NOT in ref splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.9501+7_9501+8insAGGTAAGGTAGTA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32394940"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that insertion variant in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.7806_7807insAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362523"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertTrue(inSpliceRegion)
        
        # checks that insertion variatn NOT in de novo splice donor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.794-5_794-4insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32332267"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=True, deNovo=True)
        self.assertFalse(inSpliceRegion)
        
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    def test_getVarSpliceRegionBoundsDonorBRCA2SNS(self, varInSpliceRegion, getRefSpliceDonorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given SNS variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = True
        deNovo = False

        # checks that variant in exon 16 splice donor region boundaries are returned correctly
        self.variant["Pos"] = "32356608"
        spliceDonorRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceDonorRegion["exonName"], "exon15")
        self.assertEquals(exonDonorBoundsBRCA2["exon15"]["donorStart"], spliceDonorRegion["donorStart"])
        self.assertEquals(exonDonorBoundsBRCA2["exon15"]["donorEnd"], spliceDonorRegion["donorEnd"])

    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_varInSpliceRegionAcceptorBRCA1SNS(self, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. SNS variant is correctly identified as in or NOT in a splice acceptor region
           uses multiple positions across multiple exons for BRCA1
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = False

        # checks that -21st base in intron is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43067716"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)
        
        # checks that first base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124135"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115787"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106534"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that first base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104956"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104260"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43099878"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that 4th base in exon is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43063948"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that region before exon 1 is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "431254483"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionAcceptorBRCA1SNSDeNovoTrue(self, getExonBoundaries, getVarType):
        '''Tests that function correctly identifies if variant is IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = True

        # checks that variant in an exonic portion of ref splice acceptor is marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43082566"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoAccRegion)

        # checks that variant in intronic portion of reference splice acceptor is marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104281"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoAccRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionAcceptorBRCA1SNSDeNovoFalse(self, getExonBoundaries, getVarType):
        '''Tests that function correctly identifies if SNS variant is NOT IN a de novo splice region for minus strand gene (BRCA1)'''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43049117"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

        # checks that last variant in an intron (-21) is NOT marked as being in a de novo acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115800"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

        # checks that 1st base after de novo acceptor region (+11) is NOT marked as being in a de novo acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43067685"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    def test_varInSpliceRegionAcceptorBRCA1DeletionDelins(self, getVarStrand, getVarType, getExonBoundaries):
        '''
        Tests that funciton correctly identifies deletion/delins variants as in/NOT in 
           ref and de novo splice regions for minus strand gene (BRCA1)
        '''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks that deletion/delins variant entirely in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5153-2delA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43063374"
        self.variant["Hg38_End"] = "43063375"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant partially in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.442-22_442-13delTGTTCTTTAC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43099892"
        self.variant["Hg38_End"] = "43099902"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)
        
        # checks that deletion/delins variant entirely NOT in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.302-24_302-22delAAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104282"
        self.variant["Hg38_End"] = "43104285"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that deletion/delins variant entirely in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5077_5080delGCTGinsTTCATTCTGC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43063946"
        self.variant["Hg38_End"] = "43063949"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)
    
        # checks that deletion/delins variant partially in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5341_5343delGAAinsTG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43049184"
        self.variant["Hg38_End"] = "43049186"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant entirely NOT in de novo splice accepotr region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5417delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43047692"
        self.variant["Hg38_End"] = "43047693"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertFalse(inSpliceRegion)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInSpliceRegionAcceptorBRCA1Insertion(self, getVarStrand, getExonBoundaries, getVarType):
        '''
        Tests that funciton correctly identifies insertion variants as in/NOT in 
           ref and de novo splice regions for minus strand gene (BRCA1)
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        
        # checks that insertion variant in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.81-14_81-13insA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115792"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that insertion variant NOT in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.-19-22_-19-21dupAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124136"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that insertion variant in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5083_5084insG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43063942"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)
        
        # checks that insertion variatn NOT in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.5478_5479dupGA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045791"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertFalse(inSpliceRegion)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarSpliceRegionBoundsAcceptorBRCA1SNS(self, varInSpliceRegion, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given SNS variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        donor = False
        deNovo = False

        # checks that variant in exon 21 splice acceptor region boundaries are returned correctly
        self.variant["Pos"] = "43051117"
        spliceAccRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceAccRegion["exonName"], "exon21")
        self.assertEquals(exonAcceptorBoundsBRCA1["exon21"]["acceptorStart"], spliceAccRegion["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA1["exon21"]["acceptorEnd"], spliceAccRegion["acceptorEnd"])

    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_varInSpliceRegionAcceptorBRCA2SNS(self, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. SNS variant is correctly identified as in or NOT in a splice acceptor region
           uses multiple positions across multiple exons for BRCA2
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = False

        # checks that -21st base in intron is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32357721"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that first base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316402"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32319069"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in intron counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32325075"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that first base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326101"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that middle base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326243"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that last base in exon counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326501"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inSpliceAcceptor)

        # checks that 4th base in exon is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362526"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

        # checks that region before exon 1 is NOT counted as in splice acceptor
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32315479"
        inSpliceAcceptor = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inSpliceAcceptor)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionAcceptorBRCA2SNSDeNovoTrue(self, getExonBoundaries, getVarType):
        '''Tests that function correctly identifies if variant is IN a de novo splice region for plus strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = True

        # checks that variant in an exonic portion of ref splice acceptor is marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32330919"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoAccRegion)

        # checks that variant in intronic portion of reference splice acceptor is marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379316"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertTrue(inDeNovoAccRegion)

    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInSpliceRegionAcceptorBRCA2SNSDeNovoFalse(self, getExonBoundaries, getVarType):
        '''Tests that function correctly identifies if SNS variant is NOT IN a de novo splice region for plus strand gene (BRCA2)'''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = True

        # checks that variant in an intron is NOT marked as being in a de novo splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32394934"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

        # checks that last variant in an intron (-21) is NOT marked as being in a de novo acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32354840"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

        # checks that 1st base after de novo acceptor region (+11) is NOT marked as being in a de novo acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326111"
        inDeNovoAccRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=donor, deNovo=deNovo)
        self.assertFalse(inDeNovoAccRegion)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    def test_varInSpliceRegionAcceptorBRCA2DeletionDelins(self, getVarStrand, getVarType, getExonBoundaries):
        '''
        Tests that funciton correctly identifies deletion/delins variants as in/NOT in 
           ref and de novo splice regions for plus strand gene (BRCA2)
        '''
        # Deletion and Delins variants have the same value for Pos and Hg38_Start and a different value for Hg38_End
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks that deletion/delins variant entirely in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.428delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32326102"
        self.variant["Hg38_End"] = "32326103"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant partially in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.7806-21_7806-19del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32362500"
        self.variant["Hg38_End"] = "32362503"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)
        
        # checks that deletion/delins variant entirely NOT in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.6941delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32346829"
        self.variant["Hg38_End"] = "32346830"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that deletion/delins variant entirely in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.429delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32326103"
        self.variant["Hg38_End"] = "32326104"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)
    
        # checks that deletion/delins variant partially in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.7979_7991delATGATACGGAAAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32363180"
        self.variant["Hg38_End"] = "32363193"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)

        # checks that deletion/delins variant entirely NOT in de novo splice accepotr region is correctly identified
        self.variant["pyhgvs_cDNA"] = "NM_000059.3:c.8332-21delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32370380"
        self.variant["Hg38_End"] = "32370381"
        inSpliceRegion = calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertFalse(inSpliceRegion)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInSpliceRegionAcceptorBRCA2Insertion(self, getVarStrand, getExonBoundaries, getVarType):
        '''
        Tests that funciton correctly identifies insertion variants as in/NOT in 
           ref and de novo splice regions for plus strand gene (BRCA2)
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        
        # checks that insertion variant in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.794-5_794-4insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32332267"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertTrue(inSpliceRegion)

        # checks that insertion variant NOT in ref splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.8958dupA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379754"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=False)
        self.assertFalse(inSpliceRegion)
        
        # checks that insertion variant in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.9257-2_9261dup"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32394687"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertTrue(inSpliceRegion)
        
        # checks that insertion variatn NOT in de novo splice acceptor region is correctly identified
        self.variant["HGVS_cDNA"] = "c.7816_7819dupGACA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362533"
        inSpliceRegion= calcVarPriors.varInSpliceRegion(self.variant, donor=False, deNovo=True)
        self.assertFalse(inSpliceRegion)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarSpliceRegionBoundsAcceptorBRCA2SNS(self, varInSpliceRegion, getSpliceAcceptorBoundaries):
        '''
        Tests that:
        1. Function returns correct donor boundaries for a given SNS variant (genomic position) 
        '''
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        donor = False
        deNovo = False

        # checks that variant in exon 20 splice acceptor region boundaries are returned correctly
        self.variant["Pos"] = "32370948"
        spliceAccRegion = calcVarPriors.getVarSpliceRegionBounds(self.variant, donor=donor, deNovo=deNovo)
        self.assertEquals(spliceAccRegion["exonName"], "exon20")
        self.assertEquals(exonAcceptorBoundsBRCA2["exon20"]["acceptorStart"], spliceAccRegion["acceptorStart"])
        self.assertEquals(exonAcceptorBoundsBRCA2["exon20"]["acceptorEnd"], spliceAccRegion["acceptorEnd"])

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInCIDomainEnigmaBRCA1SNS(self, getVarStrand, varInExon, getVarType):
        '''Tests that SNS variant is correctly identified as in or NOT in CI domain in BRCA1 as defined by ENIGMA rules'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks variant in BRCA 1 RING domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124089"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant in BRCA1 BRCT domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43070945"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant NOT in BRCA1 CI domain is NOT identified as in ENIGMA CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43097274"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inEnigmaCI)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInCIDomainEnigmaBRCA2SNS(self, getVarStrand, varInExon, getVarType):
        '''Tests that SNS variant is correctly identified as in or NOT in CI domain in BRCA2 as defined by ENIGMA rules'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks variant in BRCA2 DNB domain is identified as in ENIGMA CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32379809"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inEnigmaCI)

        # checks variant NOT in BRCA2 CI domain is NOT identified as in ENIGMA CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398354"
        inEnigmaCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inEnigmaCI)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInCIDomainPriorsBRCA1SNS(self, getVarStrand, varInExon, getVarType):
        '''Tests that SNS variant is correctly identified as in or NOT in CI domain in BRCA1 as defined by PRIORS webiste'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks variant in BRCA1 initiation domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124096"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA1 RING domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115746"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA1 BRCT domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43057092"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks that variant NOT in BRCA1 CI domain is NOT identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124090"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inPriorsCI)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_varInCIDomainPriorsBRCA2SNS(self, getVarStrand, varInExon, getVarType):
        '''Tests that SNS variant is correctly identified as in or NOT in CI domain in BRCA2 as defined by PRIORS webiste'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks variant in BRCA2 initiation domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316462"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA2 PALB2 domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32319092"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in BRCA2 DNB domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362561"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks variant in TR2/RAD5 domain is identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398406"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertTrue(inPriorsCI)

        # checks that variant NOT in BRCA2 CI domain is NOT identified as in PRIORS CI domain
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32336283"
        inPriorsCI = calcVarPriors.varInCIDomain(self.variant, boundaries)
        self.assertFalse(inPriorsCI)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    def test_varInCIDomainBRCA1DeletionDelins(self, getVarStrand, varInExon, getVarType):
        '''Checks that deletion/delins variants are correctly identified an in/NOT in CI domain in BRCA1'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks deletion/delins variant entirely in CI domain
        self.variant["HGVS_cDNA"] = "c.5503_5564delCGAGAGTGGGTGTTGGACAGTGTAGCACTCTACCAGTGCCAGGAGCTGGACACCTACCTGAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43045705"
        self.variant["Hg38_End"] = "43045767"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertTrue(inCIDomain)

        # checks deletion/delins variant partially in CI domain
        self.variant["HGVS_cDNA"] = "c.1_15del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124081"
        self.variant["Hg38_End"] = "43124096"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertTrue(inCIDomain)

        # checks deletion/delins variant NOT in CI domain (5' end)
        self.variant["HGVS_cDNA"] = "c.4945_4947delAGAinsTTTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43070967"
        self.variant["Hg38_End"] = "43070969"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertFalse(inCIDomain)

        # checks deletion/delins variant NOT in CI domain (3' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104873"
        self.variant["Hg38_End"] = "43104874"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertFalse(inCIDomain)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInCIDomainBRCA1Insertion(self, getVarStrand, varInExon, getVarType):
        '''Checks that insertion variants are correctly identified an in/NOT in CI domain in BRCA1'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks for large insertion variant in CI domain
        self.variant["HGVS_cDNA"] = "c.5468-11_5520dup"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045749"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertTrue(inCIDomain)

        # checks for small insertion variant in CI domain
        self.variant["HGVS_cDNA"] = "c.18_19insG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124078"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertTrue(inCIDomain)

        # checks for insertion variant NOT in CI domain (5' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124085"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertFalse(inCIDomain)

        # checks for insertion variant NOT in CI domain (3' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104258"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertFalse(inCIDomain)

    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    def test_varInCIDomainBRCA2DeletionDelins(self, getVarStrand, varInExon, getVarType):
        '''Checks that deletion/delins variants are correctly identified an in/NOT in CI domain in BRCA2'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks deletion/delins variant entirely in CI domain
        self.variant["HGVS_cDNA"] = "c.3delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316462"
        self.variant["Hg38_End"] = "32316463"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertTrue(inCIDomain)

        # checks deletion/delins variant partially in CI domain
        self.variant["HGVS_cDNA"] = "c.9556_9567delGCAAATGATCCCinsAAGTGGTCCACCCCAACTA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32396952"
        self.variant["Hg38_End"] = "32396963"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertTrue(inCIDomain)

        # checks deletion/delins variant NOT in CI domain (5' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32356431"
        self.variant["Hg38_End"] = "32356432"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertFalse(inCIDomain)

        # checks deletion/delins variant NOT in CI domain (3' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316463"
        self.variant["Hg38_End"] = "32316464"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertFalse(inCIDomain)
        
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_varInCIDomainBRCA2Insertion(self, getVarStrand, varInExon, getVarType):
        '''Checks that insertion variants are correctly identified an in/NOT in CI domain in BRCA2'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks for large insertion variant in CI domain
        self.variant["HGVS_cDNA"] = "c.9517_9518insTCTAAGTCAAATGTTTTCAAAACAATTGACATTGTTTTCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32396913"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertTrue(inCIDomain)

        # checks for small insertion variant in CI domain
        self.variant["HGVS_cDNA"] = "c.7806_7807insAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362523"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertTrue(inCIDomain)

        # checks for insertion variant NOT in CI domain (5' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316490"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "priors")
        self.assertFalse(inCIDomain)

        # checks for insertion variant NOT in CI domain (3' end)
        # this variant is not in database as of 5/14/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32396955"
        inCIDomain = calcVarPriors.varInCIDomain(self.variant, "enigma")
        self.assertFalse(inCIDomain)

    def test_varInGreyZone(self):
        '''Tests that variant is correctly identified as in the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks that BRCA1 variant is NOT considered in grey zone
        self.variant["Pos"] = "43045708"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertFalse(inGreyZone)

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks that variant before the BRCA2 grey zone is NOT identified as in BRCA2 grey zone
        self.variant["Pos"] = "32398437"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertFalse(inGreyZone)

        # checks that variant in BRCA2 grey zone is identified as in BRCA2 grey zone
        self.variant["Pos"] = "32398459"
        inGreyZone = calcVarPriors.varInGreyZone(self.variant)
        self.assertTrue(inGreyZone)
        
    def test_varAfterGreyZoneBRCA1(self):
        '''Tests that variant in BRCA1 is NOT considered as after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks that BRCA1 variant is NOT considered after grey zone
        self.variant["Pos"] = "43045689"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertFalse(afterGreyZone)

    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    def test_varAfterGreyZoneFalseBRCA2(self, varInUTR, varInGreyZone):
        '''Tests that variant in BRCA2 is correctly identified as NOT after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        self.variant["Pos"] = "32398459"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertFalse(afterGreyZone)
        
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    def test_varAfterGreyZoneFalseBRCA2(self, varInUTR, varInGreyZone):
        '''Tests that variant after BRCA2 grey zone is correctly identified as after the grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        self.variant["Pos"] = "32398489"
        afterGreyZone = calcVarPriors.varAfterGreyZone(self.variant)
        self.assertTrue(afterGreyZone)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInIntronStructuralVarsBRCA1Deletion(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                    getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # check function for deletion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.-19-22_-19-21del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124135"
        self.variant["Hg38_End"] = "43124137"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.5406+664_5468-162del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43045963"
        self.variant["Hg38_End"] = "43048457"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant entirely NOT in intron
        self.variant["pyhgvs_cDNA"] = "c.68delA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124028"
        self.variant["Hg38_End"] = "43124029"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for deletion variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.5277+1_5277+6del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43057045"
        self.variant["Hg38_End"] = "43057051"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.671-18_671-16delATT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43094875"
        self.variant["Hg38_End"] = "43094878"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInIntronStructuralVarsBRCA2Deletion(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                    getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        # check function for deletion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.6841+7_6841+8delGT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32341202"
        self.variant["Hg38_End"] = "32341204"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.7598_7617+263del283"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32356588"
        self.variant["Hg38_End"] = "32356871"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant entirely NOT in intron
        self.variant["pyhgvs_cDNA"] = "c.8756delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379317"
        self.variant["Hg38_End"] = "32379318"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)       
        self.assertFalse(inIntron)

        # check function for deletion variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.8953+5del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379519"
        self.variant["Hg38_End"] = "32379520"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for deletion variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.7008-20_7008-17del4"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32354840"
        self.variant["Hg38_End"] = "32354844"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInIntronStructuralVarsBRCA1Insertion(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                    getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # check function for large insertion variant in intron
        self.variant["HGVS_cDNA"] = "c.5333-358_5333-342dup"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43049535"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for small insertion variant in intron
        self.variant["HGVS_cDNA"] = "c.-19-22_-19-21dupAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124136"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for insertion variant NOT in intron
        self.variant["HGVS_cDNA"] = "c.2658_2659insA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43092872"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for insertion variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.441+2_441+6dupTAAAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104116"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for insertion variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.-19-2_-19-1insAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124116"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInIntronStructuralVarsBRCA2Insertion(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                     getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        # check function for large insertion variant in intron
        self.variant["HGVS_cDNA"] = "c.9501+7_9501+8insAGGTAAGGTAGTA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32394940"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for small insertion variant in intron
        self.variant["pyhgvs_cDNA"] = "NM_000059.3:c.9257-26_9257-25dupAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32394662"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for insertion variant NOT in intron
        self.variant["HGVS_cDNA"] = "c.44_45insATT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316504"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for insertion variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.516_516+1insC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326282"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for insertion variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.476-17_476-16insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326225"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_varInIntronStructuralVarsBRCA1Delins(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                    getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # check function for delins variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.301+26_301+27delinsCA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104841"
        self.variant["Hg38_End"] = "43104842"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant partially in intron
        self.variant["HGVS_cDNA"] = "c.5152+149_5193+2200delinsTTTTTTTTTTTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43061133"
        self.variant["Hg38_End"] = "43063725"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant entirely NOT in intron
        self.variant["HGVS_cDNA"] = "c.288_292delCACAGinsAACCTGT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104877"
        self.variant["Hg38_End"] = "43104881"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for delins variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.5331_5332+6delinsCAACAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43051057"
        self.variant["Hg38_End"] = "43051064"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.-19-17_-19-13delTTTCTinsAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124128"
        self.variant["Hg38_End"] = "43124132"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_varInIntronStructuralVarsBRCA2Delins(self, getVarType, varOutsideBoundaries, getExonBoundaries,
                                                    getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        # check function for delins variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.425+22_425+58delinsTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32325206"
        self.variant["Hg38_End"] = "32325242"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant partially in intron
        self.variant["HGVS_cDNA"] = "c.276_317-722delinsCCAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32319285"
        self.variant["Hg38_End"] = "32324354"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant entirely NOT in intron
        self.variant["HGVS_cDNA"] = "c.369_371delAATinsTA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32325128"
        self.variant["Hg38_End"] = "32325130"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertFalse(inIntron)

        # check function for delins variant in ref splice donor region
        self.variant["HGVS_cDNA"] = "c.9256_9256+2delinsACAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32380145"
        self.variant["Hg38_End"] = "32380147"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

        # check function for delins variant in ref splice acceptor region
        self.variant["HGVS_cDNA"] = "c.9257-19_9257-17del3insCC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32394670"
        self.variant["Hg38_End"] = "32394672"
        inIntron = calcVarPriors.varInIntronStructuralVars(self.variant)
        self.assertTrue(inIntron)

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = True)
    def test_getVarLocationSNSOutBounds(self, varOutsideBoundaries):
        '''Tests that SNS variants outside transcript boundaries are correctly identified as outside transcript boundaries'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant outside transcript boundaries (before txn start)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_Start"] = "43125600"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        # BRCA1 variant outside transcript boundaries (after txn end)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_Start"] = "43044000"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant outside transcript boundaries (before txn start)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_Start"] = "32315300"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

        # BRCA2 variant outside transcript boundaries (after txn end)
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_Start"] = "32399800"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["outBounds"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    def test_getVarLocationSNSCIDomain(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInCIDomain):
        '''
        Tests that SNS variants in either PRIORS or ENIGMA CI domain and NOT in a splice region are
        identified as in CI domain
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant in middle of ENIGMA CI domain
        self.variant["Pos"] = "43063930"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

        # BRCA1 variant in middle of PRIORS CI domain
        boundaries = "priors"
        self.variant["Pos"] = "43106502"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])
        
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in middle of ENIGMA CI domain
        self.variant["Pos"] = "32376714"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

        # BRCA2 variant in middle of PRIORS CI domain
        boundaries = "priors"
        self.variant["Pos"] = "32363207"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCI"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarLocationSNSCIDomainSpliceRegionBRCA1(self, varOutsideBoundaries, varInExon, varInCIDomain,
                                                     getRefSpliceDonorBoundaries, getSpliceAcceptorBoundaries):
        '''
        Tests that BRCA1 SNS variants in either PRIORS or ENIGMA CI domains AND in splice region are
        correctly identified as in CI domain splice region
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
                
        # BRCA1 variant in ENIGMA CI domain splice donor region
        boundaries = "enigma"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104868"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])
        
        # BRCA1 variant in PRIORS CI domain splice donor region
        boundaries = "priors"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106456"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA1 variant in ENIGMA CI domain splice acceptor region
        boundaries = "enigma"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43063373"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

        # BRCA1 variant in PRIORS CI domain splice acceptor region
        boundaries = "priors"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43057135"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarLocationSNSCIDomainSpliceRegionBRCA2(self, varOutsideBoundaries, varInExon, varInCIDomain,
                                                     getRefSpliceDonorBoundaries, getSpliceAcceptorBoundaries):
        '''
        Tests that BRCA2 SNS variants in either PRIORS or ENIGMA CI domains AND in splice region are
        correctly identified as in CI domain splice region
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # BRCA2 variant in ENIGMA CI splice donor region
        boundaries = "enigma"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32357929"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA2 variant in PRIORS CI splice donor region
        boundaries = "priors"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316527"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceDonor"])

        # BRCA2 variant in ENIGMA CI splice acceptor region
        boundaries = "enigma"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32376670"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

        # BRCA2 variant in PRIORS CI splice acceptor region
        boundaries = "priors"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32363179"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inCISpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    def test_getVarLocationSNSSpliceRegionBRCA1(self, varOutsideBoundaries, getExonBoundaries, getRefSpliceDonorBoundaries,
                                             getSpliceAcceptorBoundaries):
        '''Tests that BRCA1 SNS variants in splice regions are correctly identified as in splice regions'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"
        
        # BRCA1 variant in splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43074331"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceDonor"])
        
        # BRCA1 variant in splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43082575"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    def test_getVarLocationSNSSpliceRegionBRCA2(self, varOutsideBoundaries, getExonBoundaries, getRefSpliceDonorBoundaries,
                                             getSpliceAcceptorBoundaries):
        '''Tests that BRCA1 SNS variants in splice regions are correctly identified as in splice regions'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in splice donor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32333388"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceDonor"])
        
        # BRCA2 variant in splice acceptor region
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32329443"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inSpliceAcceptor"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    def test_getVarLocationSNSInExon(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInCIDomain):
        '''Tests that SNS variants in exons are correctly identified as in exons'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43071220"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inExon"])
        
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in exon
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32336289"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inExon"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    def test_getVarLocationSNSInUtrBRCA1(self, varOutsideBoundaries, getExonBoundaries, varInSpliceRegion, varInUTR):
        '''Tests that BRCA1 SNS variants in UTR are correctly identified as in UTR'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124138"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

        # BRCA1 variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045660"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])
        
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    def test_getVarLocationSNSInUtrBRCA2(self, varOutsideBoundaries, getExonBoundaries, varInSpliceRegion, varInUTR):
        '''Tests that BRCA2 SNS variants in UTR are correctly identified as in UTR'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in 5' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316398"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

        # BRCA2 variant in 3' UTR
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398790"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inUTR"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getVarLocationSNSInIntron(self, varOutsideBoundaries, varInExon, varInSpliceRegion):
        '''Tests that SNS variants in introns are correctly identified as in introns'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        boundaries = "enigma"

        # BRCA1 variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43071263"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inIntron"])

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"
        
        # BRCA2 variant in intron
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32344537"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inIntron"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    def test_getVarLocationSNSInGreyZone(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varInGreyZone):
        '''Tests that BRCA2 SNS variant in grey zone is correctly identified as in grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant in grey zone
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398465"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["inGreyZone"])

    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = True)
    def test_getVarLocationSNSAfterGreyZone(self, varOutsideBoundaries, varInExon, varInSpliceRegion, varAfterGreyZone):
        '''Tests that BRCA2 SNS variant after grey zone is correctly identified as after grey zone'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        boundaries = "enigma"

        # BRCA2 variant after grey zone
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398499"
        varLoc = calcVarPriors.getVarLocationSNS(self.variant, boundaries)
        self.assertEquals(varLoc, variantLocations["afterGreyZone"])

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = True)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarOutBoundsDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                          varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                          varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants outside transcript boundaries are correctly identified as outside boundaries'''
        boundaries = "enigma"

        # tests for BRCA1 deletion variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        self.variant["HGVS_cDNA"] = "c.-2617_-2616del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43127866"
        self.variant["Hg38_End"] = "43127868"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

        # tests for BRCA1 deletion variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32315226"
        self.variant["Hg38_End"] = "32315227"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = True)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarOutBoundsInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                            varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                            varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants outside transcript boundaries are correctly identified as outside boundaries'''
        boundaries = "enigma"

        # tests for BRCA1 insertion variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        self.variant["HGVS_cDNA"] = "c.*5678_*5679insAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43039999"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

        # tests for BRCA1 insertion variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32314942"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = True)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarOutBoundsDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                        varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                        varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants outside transcript boundaries are correctly identified as outside boundaries'''
        boundaries = "enigma"

        # tests for BRCA1 delins variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43043006"
        self.variant["Hg38_End"] = "43043009"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

        # tests for BRCA1 delins variant outside transcript boundaries
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32315225"
        self.variant["Hg38_End"] = "32315227"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "outside_transcript_boundaries")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, False, True, True,
                                                                  False, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, True, False, True])
    def test_getVarLocationStructuralVarInCIDomainDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                           varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                           varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in CI domain are correctly identified as in CI domain'''
        boundaries = "enigma"
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 deletion variant that is just in CI domain
        self.variant["HGVS_cDNA"] = "c.65delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124031"
        self.variant["Hg38_End"] = "43124032"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA1 deletion variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.5333-198_5387del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43049139"
        self.variant["Hg38_End"] = "43049392"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/splice_acceptor/exon/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 deletion variant that is just in CI domain
        self.variant["HGVS_cDNA"] = "c.7474_7475delGA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32356465"
        self.variant["Hg38_End"] = "32356467"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA2 deletion variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.8948_8953+5delATTCAGGTAAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379509"
        self.variant["Hg38_End"] = "32379520"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, False, True, False,
                                                                  False, False, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarInCIDomainInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                            varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                            varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants in CI domain are correctly identified as in CI domain'''
        boundaries = "enigma"
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 insertion variant that is in CI domain
        self.variant["HGVS_cDNA"] = "c.190_191insAATGTAAGGATGATATAAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43106477"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA1 insertion variant that is in CI domain and splice donor region
        self.variant["HGVS_cDNA"] = "c.5464_5465insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43047645"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 insertion variant that is in CI domain
        self.variant["HGVS_cDNA"] = "c.7675_7676insAAAC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32357799"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA2 insertion variant that is in CI domain and splice acceptor region
        self.variant["HGVS_cDNA"] = "c.7806_7807insAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32362523"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_acceptor/exon")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = True)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, False, False, True,
                                                                  False, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, True, False, True])
    def test_getVarLocationStructuralVarInCIDomainDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                         varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                         varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in CI domain are correctly identified as in CI domain'''
        boundaries = "enigma"
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 delins variant that is just in CI domain
        self.variant["HGVS_cDNA"] = "c.5208_5247delCAGAGGAGATGTGGTCAATGGAAGAAACCACCAAGGTCCAinsTC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43057082"
        self.variant["Hg38_End"] = "43057121"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA1 delins variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.5194-1_5197delinsTATT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43057132"
        self.variant["Hg38_End"] = "43057136"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_acceptor/exon/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 delins variant that is just in CI domain
        self.variant["HGVS_cDNA"] = "c.8585_8586delTAinsAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32371053"
        self.variant["Hg38_End"] = "32371054"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/exon")

        # tests for BRCA2 delins variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.9256_9256+2delinsACAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32380145"
        self.variant["Hg38_End"] = "32380147"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [False, True, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False, True, False,
                                                                  True, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect =[True, False, True, False])
    def test_getVarLocationStructuralVarInSpliceDonorDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                              varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                              varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in splice donor region are correctly identified'''
        boundaries = "enigma"
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 deletion variant that is in intronic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.670+1delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43095844"
        self.variant["Hg38_End"] = "43095845"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/intron")

        # tests for BRCA1 deletion variant that is in exonic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.4654_4673del20"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43074332"
        self.variant["Hg38_End"] = "43074352"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 deletion variant that is in intronic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.7976+3_7976+4delAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32362695"
        self.variant["Hg38_End"] = "32362697"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/intron")

        # tests for BRCA2 deletion variant that is in exonic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.7006delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32346894"
        self.variant["Hg38_End"] = "32346895"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [True, False, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False, True, False,
                                                                  True, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, True, True, False])
    def test_getVarLocationStructuralVarInSpliceDonorInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                               varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                               varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants partially or entirely in splice donor region are correctly identified'''
        boundaries = "enigma"

        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 insertion variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.75_80dupCATCTG"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "CAGATGC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124017"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon")
        
        # tests for BRCA1 insertion variant that is in intronic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.134+3_134+4insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115722"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 insertion variant that is in intronic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.681+2dupT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32329494"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/intron")

        # tests for BRCA2 insertion variant that is in exonic portion of splice donor
        self.variant["HGVS_cDNA"] = "c.516_516+1insC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326282"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [False, True])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = True)
    def test_getVarLocationStructuralVarInSpliceDonorDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                            varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                            varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in splice donor region are correctly identified'''
        boundaries = "enigma"
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 delins variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.5331_5332+6delinsCAACAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43051057"
        self.variant["Hg38_End"] = "43051064"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon/intron")
        
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 delins variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.9256_9256+1delGGinsTA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32380145"
        self.variant["Hg38_End"] = "32380146"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True, False, True,
                                                                  False, True, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, True, True, True])
    def test_getVarLocationStructuralVarInSpliceAcceptorDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                                 varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                                 varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in splice acceptor region are correctly identified'''
        boundaries = "enigma"

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # tests for BRCA2 deletion variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.7980_7984delTGATA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32363181"
        self.variant["Hg38_End"] = "32363186"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_acceptor/exon")
        
        # tests for BRCA2 deletion variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.6842-12_6842-8delATTTC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32344545"
        self.variant["Hg38_End"] = "32344550"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")
        
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # tests for BRCA1 deletion variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.81-12delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43115790"
        self.variant["Hg38_End"] = "43115791"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

        # tests for BRCA1 deletion variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.442-22_442-13delTGTTCTTTAC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43099892"
        self.variant["Hg38_End"] = "43099902"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [True, False, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True, False, True,
                                                                  False, True, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, True, True, False])
    def test_getVarLocationStructuralVarInSpliceAcceptorInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                                  varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                                  varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants partially or entirely in splice acceptor region are correctly identified'''
        boundaries = "enigma"

        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # tests for BRCA1 insertion variant that crosses a location boundary
        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104260"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_acceptor/exon")
        
        # tests for BRCA1 insertion variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.81-14_81-13insA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115792"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        # tests for BRCA2 insertion variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.476-17_476-16insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326225"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

        # tests for BRCA2 insertion variant that is in exonic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.428dupC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326103"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/exon")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [False, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True, False, True,
                                                                  False, True, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = True)
    def test_getVarLocationStructuralVarInSpliceAcceptorDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                               varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                               varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in splice acceptor region are correctly identified'''
        boundaries = "enigma"

        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # tests for BRCA1 delins variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.81-5_81-1delinsACCTTGA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43115780"
        self.variant["Hg38_End"] = "43115784"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        
        # tests for BRCA2 delins variant that is in intronic portion of splice acceptor
        self.variant["HGVS_cDNA"] = "c.68-8_68-7delinsAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32319069"
        self.variant["Hg38_End"] = "32319070"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

        # tests for BRCA2 delins variant that crosses a location boundary
        self.variant["HGVS_cDNA"] = "c.8488-1_8496del10insCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32370955"
        self.variant["Hg38_End"] = "32370964"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarInGreyZoneDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                           varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                           varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 deletion variant in grey zone is correctly identified as in grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        self.variant["HGVS_cDNA"] = "c.9945delA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398457"
        self.variant["Hg38_End"] = "32398458"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarInGreyZoneInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                            varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                            varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 insertion variant in grey zone is correctly identified as in grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398444"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarInGreyZoneDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                         varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                         varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 delins variant in grey zone is correctly identified as in grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398471"
        self.variant["Hg38_End"] = "32398474"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarAfterGreyZoneDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                              varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                              varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 deletion variant after grey zone is correctly identified as after grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        self.variant["HGVS_cDNA"] = "c.9997_9998delCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398509"
        self.variant["Hg38_End"] = "32398511"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "after_grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarAfterGreyZoneInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                               varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                               varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 insertion variant after grey zone is correctly identified as after grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        self.variant["HGVS_cDNA"] = "c.10094_10095insGAATTATATC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398607"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "after_grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarAfterGreyZoneDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                             varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                             varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that BRCA2 delins variant after grey zone is correctly identified as after grey zone'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # this variant does not exist in database as of 5/16/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398597"
        self.variant["Hg38_End"] = "32398601"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "after_grey_zone")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True, False, False,
                                                                  False, False, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, False, False, True])
    def test_getVarLocationStructuralVarInExonDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                       varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                       varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in exon are correctly identified as in an exon'''
        boundaries = "enigma"

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for deletion variant that spans multiple locations
        self.variant["HGVS_cDNA"] = "c.8488_8489delTG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32370955"
        self.variant["Hg38_End"] = "32370957"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_acceptor/exon")
        
        # checks function for deletion variant just in exon
        self.variant["HGVS_cDNA"] = "c.36delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316495"
        self.variant["Hg38_End"] = "32316496"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for deletion variant just in exon
        self.variant["HGVS_cDNA"] = "c.1327_1345delAAAAGTGAAAGAGTTCACT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43094185"
        self.variant["Hg38_End"] = "43094204"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        # checks function for deletion variant that spans multiple locations
        self.variant["HGVS_cDNA"] = "c.442-43_524del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43099797"
        self.variant["Hg38_End"] = "43099923"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False, False, False,
                                                                  False, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', return_value = False)
    def test_getVarLocationStructuralVarInExonInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                        varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                        varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants partially or entirely in exon are correctly identified as in an exon'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for insertion variant that has multiple location tags
        self.variant["HGVS_cDNA"] = "c.78_79insCATCTG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124018"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon")
        
        # checks function for insertion variant just in exon
        self.variant["HGVS_cDNA"] = "c.4838_4839insC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43071075"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for insertion variant just in exon
        self.variant["HGVS_cDNA"] = "c.4540_4541insCGAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32338895"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        # checks function for insertion variant that has multiple location tags
        self.variant["HGVS_cDNA"] = "c.6839_6840insA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32341194"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInCIDomain', side_effect =[True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False, False, False,
                                                                  False, False, True, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [False, False, False, True])
    def test_getVarLocationStructuralVarInExonDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                     varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                     varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in exon are correctly identified as in an exon'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for delins variant that spans multiple locations
        self.variant["HGVS_cDNA"] = "c.5331_5332+6delinsCAACAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43051057"
        self.variant["Hg38_End"] = "43051064"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/exon")
        
        # checks function for delins variant just in exon
        self.variant["HGVS_cDNA"] = "c.4391_4393delCTAinsTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43076579"
        self.variant["Hg38_End"] = "43076581"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for delins variant just in exon
        self.variant["HGVS_cDNA"] = "c.765_770delCACAAAinsAAACAAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32331002"
        self.variant["Hg38_End"] = "32331007"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon")

        # checks function for delins variant that spans multiple locations
        self.variant["HGVS_cDNA"] = "c.276_317-722delinsCCAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32319285"
        self.variant["Hg38_End"] = "32324354"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [False, True, True, True])
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, False, False, False])
    def test_getVarLocationStructuralVarInUTRDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                      varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                      varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in UTRs are correctly identified as in UTRs'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for deletion variant in 5' UTR
        self.variant["HGVS_cDNA"] = "c.-19-58_-19-56del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124170"
        self.variant["Hg38_End"] = "43124173"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "UTR/intron")

        # checks function for deletion variant in 3' UTR
        self.variant["HGVS_cDNA"] = "c.5574_*2del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43045675"
        self.variant["Hg38_End"] = "43045696"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for deletion variant in 5' UTR
        self.variant["HGVS_cDNA"] = "c.-7_9del16"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316453"
        self.variant["Hg38_End"] = "32316469"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

        # checks function for deletion variant in 3' UTR
        self.variant["HGVS_cDNA"] = "c.*839delT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32399608"
        self.variant["Hg38_End"] = "32399609"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [False, True, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, False, True, False])
    def test_getVarLocationStructuralVarInUTRInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                       varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                       varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants partially or entirely in UTRs are correctly identified as in UTRs'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for insertion variant in 5' UTR
        self.variant["HGVS_cDNA"] = "c.-19-55_-19-54insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124169"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "UTR/intron")

        # checks function for insertion variant in 3' UTR
        self.variant["pyhgvs_cDNA"] = "NM_007294.3:c.*1287dupC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43044390"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for insertion variant in 5' UTR
        # this variant does not exist in database as of 5/17/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32315648"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "UTR/intron")

        # checks function for insertion variant in 3' UTR
        self.variant["HGVS_cDNA"] = "c.*360dupC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32399130"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [False, True, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True, False, False,
                                                                  False, False, False, False])
    @mock.patch('calcVarPriors.varInUTR', return_value = True)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, False, True, False])
    def test_getVarLocationStructuralVarInUTRDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                    varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                    varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in UTRs are correctly identified as in UTRs'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for delins variant in 5' UTR
        self.variant["HGVS_cDNA"] = "c.-19-17_-19-13delTTTCTinsAA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43124128"
        self.variant["Hg38_End"] = "43124132"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/UTR/intron")

        # checks function for delins variant in 3' UTR
        # this variant does not exist in database as of 5/17/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43044826"
        self.variant["Hg38_End"] = "43044828"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for delins variant in 5' UTR
        self.variant["HGVS_cDNA"] = "c.-26_-25delGCinsAG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316435"
        self.variant["Hg38_End"] = "32316436"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "UTR/intron")

        # checks function for delins variant in 3' UTR
        # this variant does not exist in database as of 5/17/18
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32398787"
        self.variant["Hg38_End"] = "32398790"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "exon/UTR")
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [True, False, False, True])
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True, False, False,
                                                                  False, False, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, True, True, True])
    def test_getVarLocationStructuralVarInIntronDeletion(self, getVarType, varOutsideBoundaries, varInExon,
                                                         varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                         varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that deletion variants partially or entirely in introns are correctly identified as in a intron'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for deletion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.5406+664_5468-162del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43045963"
        self.variant["Hg38_End"] = "43048457"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/splice_acceptor/exon/intron")
        
        # checks function for deletion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.442-680_442-679del"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43100558"
        self.variant["Hg38_End"] = "43100560"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for deletion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.516+14delC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32326295"
        self.variant["Hg38_End"] = "32326296"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        # checks function for deletion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.7436-2_7437delAGAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32356425"
        self.variant["Hg38_End"] = "32356429"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/exon/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInCIDomain', return_value = False)
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, False, True, False,
                                                                  False, False, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, True, True, True])
    def test_getVarLocationStructuralVarInIntronInsertion(self, getVarType, varOutsideBoundaries, varInExon,
                                                          varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                          varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that insertion variants partially or entirely in introns are correctly identified as in a intron'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks function for insertion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.442-810_442-809insACA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43100689"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        # checks function for insertion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.301+2dupT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43104866"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_donor/intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for insertion variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.681+20_681+21insA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32329511"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        # checks function for insertion variant partially in intron
        self.variant["HGVS_cDNA"] = "c.794-5_794-4insT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32332267"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    @mock.patch('calcVarPriors.varOutsideBoundaries', return_value = False)
    @mock.patch('calcVarPriors.varInExon', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInCIDomain', side_effect = [True, False, False, False])
    @mock.patch('calcVarPriors.varInGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varAfterGreyZone', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True, False, False,
                                                                  False, False, False, True])
    @mock.patch('calcVarPriors.varInUTR', return_value = False)
    @mock.patch('calcVarPriors.varInIntronStructuralVars', side_effect = [True, True, True, True])
    def test_getVarLocationStructuralVarInIntronDelins(self, getVarType, varOutsideBoundaries, varInExon,
                                                       varInCIDomain, varInGreyZone, varAfterGreyZone,
                                                       varInSpliceRegion, varInUTR, varInIntronStructuralVars):
        '''Tests that delins variants partially or entirely in introns are correctly identified as in a intron'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        
        # checks function for delins variant partially in intron
        self.variant["HGVS_cDNA"] = "c.5152+149_5193+2200delinsTTTTTTTTTTTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43061133"
        self.variant["Hg38_End"] = "43063725"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "CI_domain/splice_donor/splice_acceptor/exon/intron")
        
        # checks function for delins variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.4987-94_4987-92delinsGCG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43067787"
        self.variant["Hg38_End"] = "43067789"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks function for delins variant entirely in intron
        self.variant["HGVS_cDNA"] = "c.8632+12_8632+19delinsATATAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32371112"
        self.variant["Hg38_End"] = "32371118"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "intron")

        # checks function for delins variant partially in intron
        self.variant["HGVS_cDNA"] = "c.9118-9_9118-8delTTinsCA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32379998"
        self.variant["Hg38_End"] = "32379999"
        varLoc = calcVarPriors.getVarLocationStructuralVar(self.variant, boundaries)
        self.assertEquals(varLoc, "splice_acceptor/intron")

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)    
    def test_getSeqLocDictBRCA1(self, getFastaSeq):
        '''
        Tests that boundary endpoints for BRCA1 are:
        1. Included in dictionary
        2. Have the correct base based on mocked sequence
        '''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        seqLocDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.assertEquals(seqLocDict[rangeStart], brca1Seq[-1])
        self.assertEquals(seqLocDict[rangeStop], brca1Seq[0])
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getSeqLocDictBRCA2(self, getFastaSeq):
        '''
        Tests that boundary endpoints for BRCA2 are:
        1. Included in dictionary
        2. Have the correct base based on mocked sequence
        '''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        seqLocDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.assertEquals(seqLocDict[rangeStart], brca2Seq[0])
        self.assertEquals(seqLocDict[rangeStop], brca2Seq[-1])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getAltSeqDictBRCA1SNS(self, getFastaSeq, getVarType):
        '''
        Tests that for given SNS variant genomic position:
        1. Reference allele is set correctly in original dictionary (refSeqDict)
        2. Alternate allele is set correctly in alternate sequence dicitonary (altSeqDict)
        '''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ATCAGATCCTAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    def test_getAltSeqDictBRCA1Deletion(self, getFastaSeq, getVarType):
        '''Tests that function works for deletion variant for minus strand gene (BRCA1)'''
        chrom = "chr17"
        strand = "-"
        rangeStart = "43097295"
        rangeStop = "43097282"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.548delG"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43097288"
        self.variant["Hg38_End"] = "43097289"
        self.variant["Ref"] = "TC"
        self.variant["Alt"] = "T"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        delStart = int(self.variant["Hg38_Start"]) + 1
        delEnd = int(self.variant["Hg38_End"])
        self.assertNotIn(delStart, altSeqDict.keys())
        self.assertNotIn(delEnd, altSeqDict.keys())

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TATGGGTGAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_getAltSeqDictBRCA1Insertion(self, getFastaSeq, getVarType):
        '''Tests that function works for insertion variant for minus strand gene (BRCA1)'''
        chrom = "chr17"
        strand = "-"
        rangeStart = "43091955"
        rangeStop = "43091945"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.3580_3581insACCC"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43091950"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "GGGGT"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTGTAGCCCA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    def test_getAltSeqDictBRCA1Delins(self, getFastaSeq, getVarType):
        '''Tests that function works for delins variant for minus strand gene (BRCA1)'''
        chrom = "chr17"
        strand = "-"
        rangeStart = "43104180"
        rangeStop = "43104170"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.389_391delACAinsTCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "43104172"
        self.variant["Hg38_End"] = "43104174"
        self.variant["Ref"] = "TGT"
        self.variant["Alt"] = "AGA"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        delStart = int(self.variant["Hg38_Start"]) + 1
        delEnd = int(self.variant["Hg38_End"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])
        self.assertNotIn(delStart, altSeqDict.keys())
        self.assertNotIn(delEnd, altSeqDict.keys())

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getAltSeqDictBRCA2SNS(self, getFastaSeq, getVarType):
        '''
        Tests that for given variant genomic position:
        1. Reference allele is set correctly in original dictionary (refSeqDict)
        2. Alternate allele is set correctly in alternate sequence dictionary (altSeqDict)
        '''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ATTTTTTGAAATTTTTAAGAC")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["del"])
    def test_getAltSeqDictBRCA2Deletion(self, getFastaSeq, getVarType):
        '''Tests that function works for deletion variant for plus strand gene (BRCA2)'''
        chrom = "chr13"
        strand = "+"
        rangeStart = "32316490"
        rangeStop = "32316510"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.37_44delGAAATTTT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32316496"
        self.variant["Hg38_End"] = "32316504"
        self.variant["Ref"] = "TGAAATTTT"
        self.variant["Alt"] = "T"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        delStart = int(self.variant["Hg38_Start"]) + 1
        delEnd = int(self.variant["Hg38_End"])
        self.assertNotIn(delStart, altSeqDict.keys())
        self.assertNotIn(delEnd, altSeqDict.keys())

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CCCTATAATTC")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_getAltSeqDictBRCA2Insertion(self, getFastaSeq, getVarType):
        '''Tests that function works for insertion variant for plus strand gene (BRCA2)'''
        chrom = "chr13"
        strand = "+"
        rangeStart = "32319130"
        rangeStop = "32319140"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.125_132dupATAATTCT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32319134"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "ATAATTCTA"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        self.assertEquals(refSeqDict[int(self.variant["Pos"])], self.variant["Ref"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "AACACAAATCA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["delins"])
    def test_getAltSeqDictBRCA2Delins(self, getFastaSeq, getVarType):
        '''Tests that function works for delins variant for plus strand gene (BRCA2)'''
        chrom = "chr13"
        strand = "+"
        rangeStart = "32331000"
        rangeStop = "32331010"
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["HGVS_cDNA"] = "c.765_770delCACAAAinsAAACAAT"
        self.variant["Pos"] = self.variant["Hg38_Start"] = "32331002"
        self.variant["Hg38_End"] = "32331007"
        self.variant["Ref"] = "CACAAA"
        self.variant["Alt"] = "AAACAAT"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        delStart = int(self.variant["Hg38_Start"]) + 1
        delEnd = int(self.variant["Hg38_End"])
        self.assertEquals(altSeqDict[int(self.variant["Pos"])], self.variant["Alt"])
        self.assertNotIn(delStart, altSeqDict.keys())
        self.assertNotIn(delEnd, altSeqDict.keys())

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    def test_getAltSeqBRCA1(self, getFastaSeq):
        '''Tests that alternate sequence string generated is correct for - strand gene (BRCA1)'''
        chrom = "chr17"
        strand = "-"
        rangeStart = 43051137
        rangeStop = 43051115
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        altSeq = calcVarPriors.getAltSeq(altSeqDict, strand)
        # reference sequence on plus strand
        brca1RefSeq = "GATCTGGAAGAAGAGAGGAAGAG"
        # reverse complement with variant included
        brca1AltSeq = "CTCTTCCTCTCTTCTTCGAGATC"
        self.assertEquals(altSeq, brca1AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getAltSeqBRCA2(self, getFastaSeq):
        '''Tests that alternate sequence string generated is correct for + strand gene (BRCA2)'''
        chrom = "chr13"
        strand = "+"
        rangeStart = 32370936
        rangeStop = 32370958
        refSeqDict = calcVarPriors.getSeqLocDict(chrom, strand, rangeStart, rangeStop)
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        altSeqDict = calcVarPriors.getAltSeqDict(self.variant, refSeqDict)
        altSeq = calcVarPriors.getAltSeq(altSeqDict, strand)
        # reference sequence on plus strand
        brca2RefSeq = "TGTGTAACACATTATTACAGTGG"
        # alternate sequence containng the alterante allele
        brca2AltSeq = "TGTGTAACCCATTATTACAGTGG"
        self.assertEquals(altSeq, brca2AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca1Seq)
    def test_getRefAltSeqsBRCA1(self, getFastaSeq):
        '''Tests that ref and alt sequence are generated correctly for - strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        rangeStart = 43051137
        rangeStop = 43051115
        self.variant["Pos"] = "43051120"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        refAltSeqs = calcVarPriors.getRefAltSeqs(self.variant, rangeStart, rangeStop)
        # reference sequence on plus strand
        brca1RefSeq = "GATCTGGAAGAAGAGAGGAAGAG"
        # reference sequence on minus strand
        brca1RefMinusSeq = "CTCTTCCTCTCTTCTTCCAGATC"
        # reverse complement with variant included
        brca1AltSeq = "CTCTTCCTCTCTTCTTCGAGATC"
        self.assertEquals(refAltSeqs["refSeq"], brca1RefSeq)
        self.assertEquals(refAltSeqs["altSeq"], brca1AltSeq)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = brca2Seq)
    def test_getRefAltSeqsBRCA2(self, getFastaSeq):
        '''Tests that ref and alt sequence are generated correctly for + strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        rangeStart = 32370936
        rangeStop = 32370958
        self.variant["Pos"] = "32370944"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        refAltSeqs = calcVarPriors.getRefAltSeqs(self.variant, rangeStart, rangeStop)
        # reference sequence on plus strand
        brca2RefSeq = "TGTGTAACACATTATTACAGTGG"
        # alternate sequence containng the alterante allele
        brca2AltSeq = "TGTGTAACCCATTATTACAGTGG"
        self.assertEquals(refAltSeqs["refSeq"], brca2RefSeq)
        self.assertEquals(refAltSeqs["altSeq"], brca2AltSeq)

    def test_getVarSeqIndexSNSDiffLengths(self):
        '''Tests that function returns "N/A" for ref and alt seqs of different lengths'''
        refSeq = "ACTGTACTC"
        altSeq = "ACTGTAACTC"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, "N/A")

    def test_getVarSeqIndexSNSDiffCases(self):
        '''Tests that function returns correct index for ref and alt seqs that have different cases'''
        refSeq = "TGTGTAACACGTAATTACAGTGG"
        altSeq = "tgtgtaacacgtaattacagtcg"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, 21)

    def test_getVarSeqIndexSNSSameCase(self):
        '''Tests that function returns correct index for ref and alt seqs that are the same case'''
        refSeq = "ctagtcgtt"
        altSeq = "ctactcgtt"
        varIndex = calcVarPriors.getVarSeqIndexSNS(refSeq, altSeq)
        self.assertEquals(varIndex, 3)

    def test_getZScore(self):
        '''
        Tests that:
        1. For score in splice donor site:
            - checks that zscore is less than zero if MaxEntScan score less than donor mean
            - checks that zscore is greater than zero if MaxEntScan score is greater than donor mean
        2. For score in splice acceptor site:
            - checks that zscore is less than zero if MaxEntScan score is less than acceptor mean
            - checks that zscore is greater than zero if MaxEntScan score is greater than acceptor mean
        '''
        # score less than donor mean of ~7.94
        maxEntScanScore = 7.8
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=True)
        self.assertLess(zScore, 0)

        # score greater than donor mean of ~7.94
        maxEntScanScore = 7.99
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=True)
        self.assertGreater(zScore, 0)

        # score less than acceptor mean of ~7.98
        maxEntScanScore = 7.9
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=False)
        self.assertLess(zScore, 0)

        # score less than acceptor mean of ~7.98
        maxEntScanScore = 8
        zScore = calcVarPriors.getZScore(maxEntScanScore, donor=False)
        self.assertGreater(zScore, 0)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"inExonicPortion": True})
    def test_varInExonicPortionTrue(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that varInExonicPortion returns True if variant is in exonic portion of window'''
        inExonicPortion = calcVarPriors.varInExonicPortion(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, donor=True)
        self.assertTrue(inExonicPortion)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"inExonicPortion": False})
    def test_varInExonicPortionFalse(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that varInExonicPortion returns False if variant is NOT in exonic portion of window'''
        inExonicPortion = calcVarPriors.varInExonicPortion(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH, donor=False)
        self.assertFalse(inExonicPortion)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 2})
    def test_getVarWindowPositionDonorFirstThree(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that function returns correct value for variant in first 3 bp of window'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=True)
        self.assertEquals(windowPos, 2)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 7})
    def test_getVarWindowPositionDonorLastSix(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that function returns correct value for variant after first 3 bp of window'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=True)
        self.assertEquals(windowPos, 7)

    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"varWindowPosition": 18})
    def test_getVarWindowPositionAcceptor(self, getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that functions returns correct value for de novo acceptor variant'''
        windowPos = calcVarPriors.getVarWindowPosition(self.variant, donor=False)
        self.assertEquals(windowPos, 18)

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonorCloseToSpliceAccBRCA1(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor site for minus strand gene (BRCA1) variant close to ref splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4097-23a>C"
        self.variant["Pos"] = "43091055"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon11")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAccCloseToSpliceAccBRCA2(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor site for plus strand gene (BRCA2) variant close to ref splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8755-22c>A"
        self.variant["Pos"] = "32379295"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon22")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSDonorCloseToSpliceDonorBRCA2(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor site for plus strand gene (BRCA2) variant close to ref splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9256+16g>A"
        self.variant["Pos"] = "32380161"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon24")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSAccCloseToSpliceDonorBRCA1(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor site for minus strand gene (BRCA1) variant close to ref splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.301+14a>G"
        self.variant["Pos"] = "43104854"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon7")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSDonor5PrimeUTRIntronBRCA2(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for plus strand gene (BRCA2) variant in intronic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-24g>C"
        self.variant["Pos"] = "32316398"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon1")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSAcc5PrimeUTRIntronBRCA1(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for minus strand gene (BRCA1) variant in intronic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-23t>G"
        self.variant["Pos"] = "43124138"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon2")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonor5PrimeUTRExonBRCA1(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for minus strand gene (BRCA1) variant in exonic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-14T>C"
        self.variant["Pos"] = "43124110"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon0")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAcc5PrimeUTRExonBRCA2(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for plus strand gene (BRCA2) variant in exonic portion of 5' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-33T>A"
        self.variant["Pos"] = "32316428"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon0")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getClosestExonNumberIntronicSNSDonorLastIntronBRCA1(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref donor for minus strand gene (BRCA1) variant in last intron of gene'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5468-25c>A"
        self.variant["Pos"] = "43045827"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=True)
        self.assertEquals(closestExonNumber, "exon23")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getClosestExonNumberIntronicSNSAccLastIntronBRCA2(self, getVarLocationSNS, getVarType, varInExon, getExonBoundaries, getVarStrand):
        '''Tests that function works to determine closest ref acceptor for plus strand gene (BRCA2) variant in last intron of gene'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9649-24g>A"
        self.variant["Pos"] = "32398138"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        closestExonNumber = calcVarPriors.getClosestExonNumberIntronicSNS(self.variant, boundaries, donor=False)
        self.assertEquals(closestExonNumber, "exon27")
                                                      
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon18")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "tctgtaagt")
    def test_getClosestSpliceSiteScoresInExonDonorBRCA1(self, varInExon, getVarLocationSNS, getVarExonNumberSNS,
                                                        getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in exon to get closest splice donor site in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5104A>G"
        self.variant["Pos"] = "43063922"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        # actualSplicePos refers to the splice donor position in the wild-type state
        actualSplicePos = 43063873
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=True,
                                                                 deNovo=False, deNovoDonorInRefAcc=True, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon18")
        self.assertEquals(closestScores["sequence"], "TCTGTAAGT")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon8")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATAAATTTTTATCTTACAGTCA")
    def test_getClosestSpliceSiteScoresInExonAccBRCA2(self, varInExon, getVarLocationSNS, getVarExonNumberSNS,
                                                      getSpliceAcceptorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in exon to get closest splice acceptor site in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.648A>G"
        self.variant["Pos"] = "32329459"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        # actualSplicePos refers to the splice acceptor position in the wild-type state
        actualSplicePos = 32329442
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon8")
        self.assertEquals(closestScores["sequence"], "CATAAATTTTTATCTTACAGTCA")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inCISpliceDonor"])
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon20")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon20',
                                                                          'donorStart': 32371098,
                                                                          'donorEnd': 32371106})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "AAGGTAAAA")
    def test_getClosestSpliceSiteScoresInRefDonorExonicBRCA2(self, varInExon, getVarLocationSNS, getVarExonNumberSNS,
                                                             getRefSpliceDonorBoundaries, varInSpliceRegion,
                                                             getVarSpliceRegionBounds, getFastaSeq):
        '''Tests function for variant in exonic portion of ref donor site to get closest splice donor site in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8631A>T"
        self.variant["Pos"] = "32371099"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        # actualSplicePos refers to the splice donor position in the wild-type state
        actualSplicePos = 32371101
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=True,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon20")
        self.assertEquals(closestScores["sequence"], "AAGGTAAAA")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inSpliceAcceptor"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43106553,
                                                                          'exonName': 'exon5',
                                                                          'acceptorEnd': 43106531})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "tctttctttataatttatagatt")
    def test_getClosestSpliceSiteScoresInRefAccIntronicBRCA1(self, getVarLocationSNS, varInExon, varInSpliceRegion,
                                                             getVarSpliceRegionBounds, getFastaSeq):
        '''
        Tests function for variant in intronic portion of ref acceptor site 
        to get closest splice acceptor site in minus strand gene (BRCA1)
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.135-11a>C"
        self.variant["Pos"] = "43106544"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        # actualSplicePos refers to the splice acceptor position in the wild-type state
        actualSplicePos = 43106534
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False,
                                                                 deNovo=False, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon5")
        self.assertEquals(closestScores["sequence"], "TCTTTCTTTATAATTTATAGATT")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32325056,
                                                                          'exonName': 'exon4',
                                                                          'acceptorEnd': 32325085})
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "GAATTATTGTACTGTTTCAGGAA")
    def test_getClosestSpliceSiteScoresInDeNovoAccBRCA2(self, getVarLocationSNS, varInExon, varInSpliceRegion,
                                                        getVarSpliceRegionBounds, getFastaSeq):
        '''Tests function for variant in exon to get closest splice acceptor site for de novo acceptor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.320G>C"
        self.variant["Pos"] = "32325079"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        # actualSplicePos refers to the splice acceptor position in the wild-type state
        actualSplicePos = 32325075
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=False,
                                                                 deNovo=True, deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon4")
        self.assertEquals(closestScores["sequence"], "GAATTATTGTACTGTTTCAGGAA")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CAAGTAAGT")
    def test_getClosestSpliceSiteScoresInIntronDonorBRCA1(self, varInExon, getVarLocationSNS, getClosestExonNumberIntronicSNS,
                                                          getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in intron to get closest splice donor site for a de novo donor in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.135-24t>C"
        self.variant["Pos"] = "43106557"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        # actualSplicePos refers to the splice donor position in the wild-type state
        actualSplicePos = 43115725
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=True, deNovo=False,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon3")
        self.assertEquals(closestScores["sequence"], "CAAGTAAGT")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon26")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TTTTCCACTTATTTTCTTAGAAT")
    def test_getClosestSpliceSiteScoresInIntronAccBRCA2(self, varInExon, getVarLocationSNS, getClosestExonNumberIntronicSNS,
                                                        getSpliceAcceptorBoundaries, varInSpliceRegion,getFastaSeq):
        '''Tests function for variant in intron to gest closest splice acceptor site for a de novo acceptor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9501+18c>T"
        self.variant["Pos"] = "32394951"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        # actualSplicePos refers to the splice acceptor position in the wild-type state
        actualSplicePos = 32396897
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False, deNovo=True,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon26")
        self.assertEquals(closestScores["sequence"], "TTTTCCACTTATTTTCTTAGAAT")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon1")
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CGGGTTAGT")
    def test_getClosestSpliceSiteScoresInUTRDonorBRCA2(self, varInExon, getVarLocationSNS, getClosestExonNumberIntronicSNS,
                                                       getRefSpliceDonorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in UTR to get closest splice donor site for a de novo donor in plus strand gene (BRCA2)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-25t>A"
        self.variant["Pos"] = "32316397"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        # actualSplicePos refers to the splice donor position in the wild-type state
        actualSplicePos = 32315668
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, STD_DE_NOVO_OFFSET, donor=True, deNovo=False,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon1")
        self.assertEquals(closestScores["sequence"], "CGGGTTAGT")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon2")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "gtttttctaatgtgttaaagttc")
    def test_getClosestSpliceSiteScoresInUTRAccBRCA1(self, varInExon, getVarLocationSNS, getClosestExonNumberIntronicSNS,
                                                     getSpliceAcceptorBoundaries, varInSpliceRegion, getFastaSeq):
        '''Tests function for variant in UTR to get closest splice acceptor site for a de novo acceptor in minus strand gene (BRCA1)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-25t>G"
        self.variant["Pos"] = "43124140"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        # actualSplicePos refers to the splice acceptor position in the wild-type state
        actualSplicePos = 43124116
        deNovoOffset = 0
        closestScores = calcVarPriors.getClosestSpliceSiteScores(self.variant, deNovoOffset, donor=False, deNovo=True,
                                                                 deNovoDonorInRefAcc=False, testMode=True)
        self.assertEquals(closestScores["exonName"], "exon2")
        self.assertEquals(closestScores["sequence"], "GTTTTTCTAATGTGTTAAAGTTC")
        self.assertEquals(closestScores["genomicSplicePos"], actualSplicePos)

    def test_isCIDomainInRegionBRCA1(self):
        '''
        Tests that region overlap is identified correctly for a variant on minus strand gene (BRCA1)
        '''
        self.variant["Gene_Symbol"] = "BRCA1"

        boundaries = "enigma"
        # region that includes ENIGMA BRCT domain
        regionStart = 43067625
        regionEnd = 43063950
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertTrue(CIDomainInRegion)

        # region that does not include any PRIORS CI domains
        boundaries = "priors"
        regionStart = 43095923
        regionEnd = 43095857
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertFalse(CIDomainInRegion)

    def test_isCIDomainInRegionBRCA2(self):
        '''
        Tests that region overlap is identified correctly for a variant on plus strand gene (BRCA2)
        '''
        self.variant["Gene_Symbol"] = "BRCA2"

        # region that does not include any ENIGMA CI domains
        boundaries = "enigma"
        regionStart = 32319089
        regionEnd = 32325063
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertFalse(CIDomainInRegion)

        # region that includeds PRIORS DNB domain
        boundaries = "priors"
        regionStart = 32379502
        regionEnd = 32379751
        CIDomainInRegion = calcVarPriors.isCIDomainInRegion(regionStart, regionEnd, boundaries, self.variant["Gene_Symbol"])
        self.assertTrue(CIDomainInRegion)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthDonorInExonBRCA1(self, varInExon, getVarExonNumberSNS, getExonBoundaries, getVarStrand):
        '''Tests that exon length for variant in exon is correctly calculated for minus strand (BRCA1) exon'''
        self.variant["Gene_Symbol"] = "BRCA1"
        exon9PlusSeq = "CTGCAATAAGTTGCCTTATTAACGGTATCTTCAGAAGAATCAGATC"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon9PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthAccInExonBRCA2(self, varInExon, getVarExonNumberSNS, getExonBoundaries, getVarStrand):
        '''Tests that exon length for variant in exon is correctly calculated for plus strand (BRCA2) exon'''
        self.variant["Gene_Symbol"] = "BRCA2"
        exon5PlusSeq = "TCCTGTTGTTCTACAATGTACACATGTAACACCACAAAGAGATAAGTCAG"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon5PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon8',
                                                                          'donorStart': 32329490,
                                                                          'donorEnd': 32329498})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthDonorInIntronicRefDonorBRCA2(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds,
                                                          getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32329494"
        exon8PlusSeq = "TCAGAAATGAAGAAGCATCTGAAACTGTATTTCCTCATGATACTACTGCT"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon8PlusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43104976,
                                                                          'exonName': 'exon6',
                                                                          'acceptorEnd': 43104954})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthAccInIntronicRefAccBRCA1(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds,
                                                      getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43104959"
        exon6MinusSeq = "gagcctacaagaaagtacgagatttagtcaacttgttgaagagctattgaaaatcatttgtgcttttcagcttgacacaggtttggagt"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon6MinusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    def test_getRefExonLengthDonorInIntronBRCA1(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS,
                                                getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43115715"
        exon3MinusSeq = "tctggagttgatcaaggaacctgtctccacaaagtgtgaccacatattttgcaa"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=True)
        self.assertEquals(refExonLength, len(exon3MinusSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon13")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    def test_getRefExonLengthAccInIntronBRCA2(self, varInExon, varInSpliceRegion, getClosstExonNumberIntronicSNS,
                                              getExonBoundaries, getVarStrand):
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32346804"
        exon13PlusSeq = "GCACAATAAAAGATCGAAGATTGTTTATGCATCATGTTTCTTTAGAGCCGATTACCTGTGTACCCTTTCG"
        refExonLength = calcVarPriors.getRefExonLength(self.variant, donor=False)
        self.assertEquals(refExonLength, len(exon13PlusSeq))

    def test_getNewSplicePositionBRCA1DonorInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max donor MES in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43104189"
        varWindowPos = 3
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 3, cut will occur after variant
        actualNewSplicePos = 43104189
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA1AccInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max acceptor MES in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43095922"
        varWindowPos = 23
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 23, cut will occur 3 bases to the left of the variant
        actualNewSplicePos = 43095925
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA1DonorNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max donor MES NOT in exonic portion'''
        varStrand = "-"
        inExonicPortion = False
        varGenPos = "43104249"
        varWindowPos = 6
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 6, cut will occur 3 bases to the left of the variant
        actualNewSplicePos = 43104252
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA1AccNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for minus strand (BRCA1) variant with max acceptor MES NOT in exonic portion'''
        varStrand = "-"
        inExonicPortion = True
        varGenPos = "43063373"
        varWindowPos = 19
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 19, cut will occur 1 base to the right of the variant
        actualNewSplicePos = 43063372
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA2DonorInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for plus strand (BRCA2) variant with max donor MES in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32354881"
        varWindowPos = 2
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 2, cut will occur 1 base to the right of the variant
        actualNewSplicePos = 32354882
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA2AccInExonicPortion(self):
        '''Tests that new splice position is calcualted correctly for plus strand (BRCA2) variant with max acceptor MES in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32326500"
        varWindowPos = 21
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 21, cut will occur before variant
        actualNewSplicePos = 32326499
        self.assertEquals(newSplicePos, actualNewSplicePos)
        
    def test_getNewSplicePositionBRCA2DonorNotInExonicPortion(self):
        '''Tests that new splice position is calculated correctly for plus strand (BRCA2) variant with max donor MES NOT in exonic portion'''
        varStrand = "+"
        inExonicPortion = False
        varGenPos = "32326277"
        varWindowPos = 8
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_DONOR_INTRONIC_LENGTH, donor=True)
        # because varWindowPos == 8, cut will occur 5 bases to the left of the variant
        actualNewSplicePos = 32326272
        self.assertEquals(newSplicePos, actualNewSplicePos)

    def test_getNewSplicePositionBRCA2AccNotInExonicPortion(self):
        '''Tests that new splice position is calculated correclty for plus strand (BRCA2) variant with max acceptor MES NOT in exonic portion'''
        varStrand = "+"
        inExonicPortion = True
        varGenPos = "32332274"
        varWindowPos = 5
        newSplicePos = calcVarPriors.getNewSplicePosition(varGenPos, varStrand, varWindowPos, inExonicPortion,
                                                          STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH, donor=False)
        # because varWindowPos == 5, cut will occur 15 bases to the right of the variant
        actualNewSplicePos = 32332289
        self.assertEquals(newSplicePos, actualNewSplicePos)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon21")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -9.9,
                                                                                       'altMaxEntScanScore': -7.45,
                                                                                       'altZScore': -6.6071787973194605,
                                                                                       'inExonicPortion': True,
                                                                                       'varWindowPosition': 2,
                                                                                       'refZScore': -7.659134374464476})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43051109)
    def test_getAltExonLengthDonorInExonBRCA1(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a minus strand (BRCA1) variant in exon'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.5285G>C"
        expectedCutSeq = "ATCTTCACG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon21")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCTTCTTCCAGATCTTCAAGGGG',
                                                                                       'varWindowPosition': 19,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -6.62,
                                                                                       'altMaxEntScanScore': 1.34,
                                                                                       'refSeq': 'TCTTCTTCCAGATCTTCAGGGGG',
                                                                                       'varStart': 18,
                                                                                       'altZScore': -2.730415411121484,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.001206083376349})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43051109)
    def test_getAltExonLengthAccInExonBRCA1(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a minus strand (BRCA1) variant in exon'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.5285G>A"
        expectedCutSeq = "GGGCTAGAAATCTGTTGCTATGGGCCCTTCACCAACATGCCCACAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon3',
                                                                          'donorStart': 43115728,
                                                                          'donorEnd': 43115720})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGAAGTT',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -10.25,
                                                                                       'altMaxEntScanScore': -1.75,
                                                                                       'refSeq': 'AAGTAAGTT',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -4.159771944369834,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -7.809413742628048})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43115725)
    def test_getAltExonLengthDonorInRefDonorBRCA1(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds, getExonBoundaries,
                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a minus strand (BRCA1) variant in a ref donor site'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.134+2t>G"
        expectedCutSeq = "TCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43063393,
                                                                          'exonName': 'exon19',
                                                                          'acceptorEnd': 43063371})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATGTAACCTGTCTTTTCTATGAG',
                                                                                       'varWindowPosition': 23,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 1.71,
                                                                                       'altMaxEntScanScore': 1.0,
                                                                                       'refSeq': 'ATGTAACCTGTCTTTTCTATGAT',
                                                                                       'varStart': 22,
                                                                                       'altZScore': -2.8701225503886514,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.5783811713307427})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43063385)
    def test_getAltExonLengthAccInRefAccBRCA1(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a minus strand (BRCA1) variant in a ref acceptor site'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.5153-9t>G"
        expectedCutSeq = "GATCTCTTTAGGGGTGACCCAGTCTATTAAAGAAAGAAAAATGCTGAATGAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))
        
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCAATGAGA',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -13.67,
                                                                                       'altMaxEntScanScore': -5.49,
                                                                                       'refSeq': 'TCAAAGAGA',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -5.765614335603449,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -9.277857854397825})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097236)
    def test_getAltExonLengthDonorInIntronBRCA1(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS, getExonBoundaries,
                                                getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a minus strand (BRCA1) variant in an intron'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.593+10a>T"
        expectedCutSeq = "GATCTGATTCTTCTGAAGATACCGTTAATAAGGCAACTTATTGCAGGTGAGTCA"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GAAAACTTTTATTGATTTAGTTT',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.49,
                                                                                       'altMaxEntScanScore': 5.11,
                                                                                       'refSeq': 'GAAAACTTTTATTGATTTATTTT',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -1.1813097786590665,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.715078595416835})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097312)
    def test_getAltExonLengthAccInIntronBRCA1(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a minus strand (BRCA1) variant in an intron'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.548-23t>G"
        expectedCutSeq = "TTTTTGGGGGGAAATTTTTTAGGATCTGATTCTTCTGAAGATACCGTTAATAAGGCAACTTATTGCAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))
        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon13")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'refMaxEntScanScore': -9.89,
                                                                                       'altMaxEntScanScore': -1.7,
                                                                                       'altZScore': -4.13830346320361,
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refZScore': -7.65484067823123})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32346831)
    def test_getAltExonLengthDonorInExonBRCA2(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a plus strand (BRCA2) variant in exon'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.6943A>G"
        expectedCutSeq = "GCACA"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTTTTATTTTAGTCCTGTAGTTC',
                                                                                       'varWindowPosition': 19,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -7.44,
                                                                                       'altMaxEntScanScore': 0.93,
                                                                                       'refSeq': 'GTTTTATTTTAGTCCTGTTGTTC',
                                                                                       'varStart': 18,
                                                                                       'altZScore': -2.8988857849436567,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.338146831020695})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326108)
    def test_getAltExonLengthAccInExonBRCA2(self, varInExon, getVarExonNumberSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a plus strand (BRCA2) variant in exon'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.432T>A"
        expectedCutSeq = "TTCTACAATGTACACATGTAACACCACAAAGAGATAAGTCAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon6',
                                                                          'donorStart': 32326280,
                                                                          'donorEnd': 32326288})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GAAGGTAAT',
                                                                                       'varWindowPosition': 9,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -17.7,
                                                                                       'altMaxEntScanScore': -12.24,
                                                                                       'refSeq': 'GAAGGTAAA',
                                                                                       'varStart': 8,
                                                                                       'altZScore': -8.663859293043796,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -11.008217436395542})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326281)
    def test_getAltExonLengthDonorInRefDonorBRCA2(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds, getExonBoundaries,
                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a plus strand (BRCA2) variant in a ref donor site'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.516+5a>T"
        expectedCutSeq = "TGGTATGTGGGAGTTTGTTTCATACACCAAAGTTTGTGAA"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32329423,
                                                                          'exonName': 'exon8',
                                                                          'acceptorEnd': 32329445})
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AATTTTTATCTTACAATCAGAAA',
                                                                                       'varWindowPosition': 16,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.56,
                                                                                       'altMaxEntScanScore': 5.4,
                                                                                       'refSeq': 'AATTTTTATCTTACAGTCAGAAA',
                                                                                       'varStart': 15,
                                                                                       'altZScore': -1.062147806931188,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.5111317776144793})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32329446)
    def test_getAltExonLengthAccInRefAccBRCA2(self, varInExon, varInSpliceRegion, getVarSpliceRegionBounds, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a plus strand (BRCA2) variant in a ref acceptor site'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.632-1g>A"
        expectedCutSeq = "AAATGAAGAAGCATCTGAAACTGTATTTCCTCATGATACTACTGCT"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon13")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CAGGTTTAA',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -16.98,
                                                                                       'altMaxEntScanScore': 1.88,
                                                                                       'refSeq': 'CATGTTTAA',
                                                                                       'varStart': 2,
                                                                                       'altZScore': -2.6011602117019152,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -10.699071307601905})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32346905)
    def test_getAltExonLengthDonorInIntronBRCA2(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS, getExonBoundaries,
                                                getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo donor for a plus strand (BRCA2) variant in an intron'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.7007+9t>G"
        expectedCutSeq = "GCACAATAAAAGATCGAAGATTGTTTATGCATCATGTTTCTTTAGAGCCGATTACCTGTGTACCCTTTCGGTAAGACAT"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=True)
        self.assertEquals(altExonLength, len(expectedCutSeq))

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon5")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTTTTTTAAAATAACCTAAGCGA',
                                                                                       'varWindowPosition': 21,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 2.4,
                                                                                       'altMaxEntScanScore': 0.42,
                                                                                       'refSeq': 'GTTTTTTAAAATAACCTAAGGGA',
                                                                                       'varStart': 20,
                                                                                       'altZScore': -3.1084464938444083,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.29485785928855})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326077)
    def test_getAltExonLengthAccInIntronBRCA2(self, varInExon, varInSpliceRegion, getClosestExonNumberIntronicSNS, getExonBoundaries,
                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition):
        '''Tests that new exon length is correctly calculated for a de novo acceptor for a plus strand (BRCA2) variant in an intron'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.426-23g>C"
        expectedCutSeq = "GGATTTGCTTTGTTTTATTTTAGTCCTGTTGTTCTACAATGTACACATGTAACACCACAAAGAGATAAGTCAG"
        altExonLength = calcVarPriors.getAltExonLength(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                       deNovoDonorInRefAcc=False, donor=False)
        self.assertEquals(altExonLength, len(expectedCutSeq))
        

    def test_compareRefAltExonLengths(self):
        '''Tests that function correctly determines if ref and alt exons are in same reading frame'''
        # ref and alt exons that share the same reading frame
        refLength = 45
        altLength = 33
        inFrame = calcVarPriors.compareRefAltExonLengths(refLength, altLength)
        self.assertTrue(inFrame)

        # ref and alt exons that do NOT share the smae reading frame
        refLength = 162
        altLength = 103
        inFrame = calcVarPriors.compareRefAltExonLengths(refLength, altLength)
        self.assertFalse(inFrame)

    @mock.patch('calcVarPriors.getRefExonLength', return_value = 45)
    @mock.patch('calcVarPriors.getAltExonLength', return_value = 30)
    @mock.patch('calcVarPriors.compareRefAltExonLengths', return_value = True)    
    def test_isSplicingWindowInFrameTrue(self, getRefExonLength, getAltExonLength, compareRefAltExonLengths):
        '''Tests that if splicing window is in frame, function returns true'''
        inFrame = calcVarPriors.isSplicingWindowInFrame(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                        deNovoDonorInRefAcc=False, donor=True)
        self.assertTrue(inFrame)
        
    @mock.patch('calcVarPriors.getRefExonLength', return_value = 45)
    @mock.patch('calcVarPriors.getAltExonLength', return_value = 29)
    @mock.patch('calcVarPriors.compareRefAltExonLengths', return_value = False)    
    def test_isSplicingWindowInFrameFalse(self, getRefExonLength, getAltExonLength, compareRefAltExonLengths):
        '''Tests that if splicing window is NOT in frame, function returns false'''
        inFrame = calcVarPriors.isSplicingWindowInFrame(self.variant, STD_EXONIC_PORTION, STD_ACC_INTRONIC_LENGTH,
                                                        deNovoDonorInRefAcc=False, donor=False)
        self.assertFalse(inFrame)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon16")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGAATTT',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -7.31,
                                                                                       'altMaxEntScanScore': -7.32,
                                                                                       'refSeq': 'GAAGAATTT',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -6.551360746287276,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.547067050054031})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43070934)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInExonBRCA1(self, varInExon, getVarStrand, getVarExonNumberSNS,
                                                                               getExonBoundaries, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in an exon
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type donor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4978G>A"
        self.variant["Pos"] = "43070936"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon6")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATTTAATTTCAGGAGCCTAGAAG',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -16.85,
                                                                                       'altMaxEntScanScore': -8.78,
                                                                                       'refSeq': 'ATTTAATTTCAGGAGCCTACAAG',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -6.888757321073649,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -10.204747361914952})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43104949)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInExonBRCA1(self, varInExon, getVarStrand, getVarExonNumberSNS,
                                                                             getExonBoundaries, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                             getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in an exon
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type acceptor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.220C>G"
        self.variant["Pos"] = "43104949"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertFalse(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon15',
                                                                          'donorStart': 43074333,
                                                                          'donorEnd': 43074325})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTAGTATTT',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -12.92,
                                                                                       'altMaxEntScanScore': -4.74,
                                                                                       'refSeq': 'GTAATATTT',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -5.443587118110077,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.955830636904453})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43074328)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInRefDonorBRCA1(self, varInExon, varInSpliceRegion,
                                                                                   getVarSpliceRegionBounds, getVarStrand,
                                                                                   getExonBoundaries,
                                                                                   getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                   getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in reference donor
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type donor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4675+4a>G"
        self.variant["Pos"] = "43074327"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43124135,
                                                                          'exonName': 'exon2',
                                                                          'acceptorEnd': 43124113})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATATATATATGTTTTTCTAATTT',
                                                                                       'varWindowPosition': 22,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -1.75,
                                                                                       'altMaxEntScanScore': -1.87,
                                                                                       'refSeq': 'ATATATATATGTTTTTCTAATGT',
                                                                                       'varStart': 21,
                                                                                       'altZScore': -4.04941516714386,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.0001067650495665})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43124126)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInRefAccBRCA1(self, varInExon, varInSpliceRegion,
                                                                               getVarSpliceRegionBounds, getVarStrand,
                                                                               getExonBoundaries,
                                                                               getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in reference acceptor
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type acceptor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-9g>T"
        self.variant["Pos"] = "43124124"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertFalse(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon8")
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATGTTTTTT',
                                                                                       'varWindowPosition': 2,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -11.16,
                                                                                       'altMaxEntScanScore': -10.36,
                                                                                       'refSeq': 'AGGTTTTTT',
                                                                                       'varStart': 1,
                                                                                       'altZScore': -7.856644401193742,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.20014009985334})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43099761)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInIntronBRCA1(self, varInExon, varInSpliceRegion,
                                                                                 getClosestExonNumberIntronicSNS, getVarStrand,
                                                                                 getExonBoundaries,
                                                                                 getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                 getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in intron
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type donor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.547+13g>T"
        self.variant["Pos"] = "43099762"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertFalse(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon20")
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca1Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCTTTCTCTTATCCTGATAGGTT',
                                                                                       'varWindowPosition': 19,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 3.13,
                                                                                       'altMaxEntScanScore': 11.09,
                                                                                       'refSeq': 'TCTTTCTCTTATCCTGATGGGTT',
                                                                                       'varStart': 18,
                                                                                       'altZScore': 1.2758922590399404,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.994898413214925})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43057157)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInIntronBRCA1(self, varInExon, varInSpliceRegion,
                                                                               getClosestExonNumberIntronicSNS, getVarStrand,
                                                                               getExonBoundaries,
                                                                               getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in intron
          is correct for a minus strand (BRCA1) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type acceptor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5194-23g>A"
        self.variant["Pos"] = "43057158"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon4")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGTGTAAGG',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -2.99,
                                                                                       'altMaxEntScanScore': 5.2,
                                                                                       'refSeq': 'AGTGAAAGG',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -1.175653062264589,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.69219027729221})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32325179)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInExonBRCA2(self, varInExon, getVarStrand, getVarExonNumberSNS,
                                                                               getExonBoundaries, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in an exon
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type donor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.422A>T"
        self.variant["Pos"] = "32325181"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertFalse(isDivisible)
        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTTTTTTTAAATAGATTTAGAAC',
                                                                                       'varWindowPosition': 21,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 2.17,
                                                                                       'altMaxEntScanScore': 0.42,
                                                                                       'refSeq': 'TTTTTTTTAAATAGATTTAGGAC',
                                                                                       'varStart': 20,
                                                                                       'altZScore': -3.1084464938444083,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.3893656299692805})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32319082)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInExonBRCA2(self, varInExon, getVarStrand, getVarExonNumberSNS,
                                                                             getExonBoundaries, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                             getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in an exon
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type acceptor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.74G>A"
        self.variant["Pos"] = "32319083"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon4',
                                                                          'donorStart': 32325182,
                                                                          'donorEnd': 32325190})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTGATGAAG',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -6.49,
                                                                                       'altMaxEntScanScore': -8.55,
                                                                                       'refSeq': 'ATGATGAAG',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -7.079485382976406,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.194983958927946})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32325189)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInRefDonorBRCA2(self, varInExon, varInSpliceRegion,
                                                                                   getVarSpliceRegionBounds, getVarStrand,
                                                                                   getExonBoundaries,
                                                                                   getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                   getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in reference donor
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type donor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.425+3a>G"
        self.variant["Pos"] = "32325187"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertFalse(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32363159,
                                                                          'exonName': 'exon18',
                                                                          'acceptorEnd': 32363181})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATATGCATTTTTGTTTTCAGTTT',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 1.13,
                                                                                       'altMaxEntScanScore': 9.2,
                                                                                       'refSeq': 'ATATGCATTTTTGTTTTCACTTT',
                                                                                       'varStart': 19,
                                                                                       'altZScore': 0.49928492605480246,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.816705114786499})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32363172)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInRefAccBRCA2(self, varInExon, varInSpliceRegion,
                                                                               getVarSpliceRegionBounds, getVarStrand,
                                                                               getExonBoundaries,
                                                                               getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in reference acceptor
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type acceptor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7977-7c>G"
        self.variant["Pos"] = "32363172"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon25")
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGGGTACTT',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.36,
                                                                                       'altMaxEntScanScore': 5.15,
                                                                                       'refSeq': 'AGGTTACTT',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -1.1971215434308138,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.851057037922273})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32394939)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeDonorInIntronBRCA2(self, varInExon, varInSpliceRegion,
                                                                                 getClosestExonNumberIntronicSNS, getVarStrand,
                                                                                 getExonBoundaries,
                                                                                 getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                 getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo donor in intron
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in intronic portion of window
            2. AND distance between de novo and wild-type donor is divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9501+7t>G"
        self.variant["Pos"] = "32394940"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=True)
        self.assertTrue(isDivisible)

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getClosestExonNumberIntronicSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getExonBoundaries', return_value = brca2Exons)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TGTCACTGGTTAAAACTAAGCTG',
                                                                                       'varWindowPosition': 21,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 1.43,
                                                                                       'altMaxEntScanScore': -1.07,
                                                                                       'refSeq': 'TGTCACTGGTTAAAACTAAGGTG',
                                                                                       'varStart': 20,
                                                                                       'altZScore': -3.7206924865152304,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.693434109550763})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32319054)
    def test_isDeNovoWildTypeSplicePosDistanceDivisibleByThreeAccInIntronBRCA2(self, varInExon, varInSpliceRegion,
                                                                               getClosestExonNumberIntronicSNS, getVarStrand,
                                                                               getExonBoundaries,
                                                                               getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getNewSplicePosition):
        '''
        Tests that comparsion between de novo and wild-type splice position for de novo acceptor in intron
          is correct for a plus strand (BRCA2) variant that:
            1. has highest scoring window with variant in exonic portion of window
            2. AND distance between de novo and wild-type acceptor is NOT divisble by 3
        '''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.68-22g>C"
        self.variant["Pos"] = "32319055"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        isDivisible = calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree(self.variant, STD_EXONIC_PORTION,
                                                                                      STD_ACC_INTRONIC_LENGTH,
                                                                                      deNovoDonorInRefAcc=False, donor=False)
        self.assertFalse(isDivisible)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSInLastExon(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon):
        '''Tests that variant in last exon is assigned correct prior prob and splice rescue flags'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], "N/A")
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], "N/A")
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "N/A")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")    
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSInExonicPortion(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon, varInExonicPortion):
        '''Tests that variant in exonic portion of highest scoring window is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], "-")
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 1)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], "-")
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSFrameshift(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                           varInExonicPortion, isSplicingWindowInFrame):
        '''Tests that variant that causes a frameshift is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], "-")
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon20")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 6)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSCIRegionEnigma(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                               varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                               getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                               isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Tests that variant that truncates part of ENGIMA CI domain is assigned correct prior prob and splice rescue flag'''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 1)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")    
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon2")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 7)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSCIRegionPriors(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                               varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                               getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                               isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Tests that variant that truncates part of PRIORS CI domain is assigned correct prior prob and splice rescue flag'''
        boundaries = "priors"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 1)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")
        
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon6")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 4)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSNotDivisible(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                             varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                             getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                             isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''
        Tests that variant that causes a frameshift (due to difference de novo vs wild-type splice position) 
        is assigned correct prior prob and splice rescue flag
        '''
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 1)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon11")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 6)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TAGAATAGC',
                                                                                       'varWindowPosition': 6,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -11.55,
                                                                                       'altMaxEntScanScore': -13.79,
                                                                                       'refSeq': 'TAGAACAGC',
                                                                                       'varStart': 5,
                                                                                       'altZScore': -9.329382209196764,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.367594252949893})
    def test_getPriorProbSpliceRescueNonsenseSNSAltLessRef(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                           varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                           getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                           isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                           getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests function for in-frame variant that does not disrupt CI domain but altZScore < refZScore so no splice rescue'''
        boundaries = "enigma"
        self.variant["HGVS_cDNA"] = "c.3403C>T"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 9)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGTCTGT',
                                                                                       'varWindowPosition': 9,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -6.35,
                                                                                       'altMaxEntScanScore': -1.85,
                                                                                       'refSeq': 'AAAGTCTGA',
                                                                                       'varStart': 8,
                                                                                       'altZScore': -4.202708906702284,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.134872211662516})
    def test_getPriorProbSpliceRescueNonsenseSNSAltGreaterRefLowMES(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                                    varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                                    getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                                    isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests function for in-frame variant that does not disrupt CI domain but altZScore > refZScore and altMES < 6.2 so no splice rescue'''        
        boundaries = "enigma"
        self.variant["HGVS_cDNA"] = "c.721A>T"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 7)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"altMaxEntScanScore": 6.5,
                                                                                       "refMaxEntScanScore": 1.2,
                                                                                       "altZScore": -0.6174725519427445,
                                                                                       "refZScore": -2.8931315555625723})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9196706995589503,
                                                                            'sequence': 'CAAGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43115725,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon3',
                                                                            'maxEntScanScore': 10.08})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSAltGreaterRefMidMESLessClosest(self, getVarConsequences, varInExon,
                                                                               varInIneligibleDeNovoExon,
                                                                               varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                                               getVarExonNumberSNS, getSpliceAcceptorBoundaries,
                                                                               getVarWindowPosition,
                                                                               isCIDomainInRegion,
                                                                               isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                               getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                               getClosestSpliceSiteScores, varInSpliceRegion):
        '''
        Tests function for in-frame FICTIONAL variant that does not disrupt CI domain where altZScore > refZScore and 6.2 <= altMES <= 8.5 
        but altZScore < closestRefZScore (closestRef because not in a ref splice donor site)  so no splice rescue
        '''
        # this example is NOT based on a real variant
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon12")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 4)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"altMaxEntScanScore": 8.6,
                                                                                       "refMaxEntScanScore": 6.88,
                                                                                       "altZScore": 0.28420365703869643,
                                                                                       "refZScore": -0.4543120950794362})
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.3516946078276324,
                                                                            'sequence': 'ATGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32344654,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon12',
                                                                            'maxEntScanScore': 4.79})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {"altZScore": -2.098797752412255})
    def test_getPriorProbSpliceRescueNonsenseSNSAltGreaterRefMidMESGreaterClosest(self, getVarConsequences, varInExon,
                                                                                  varInIneligibleDeNovoExon,
                                                                                  varInExonicPortion, isSplicingWindowInFrame,
                                                                                  getVarStrand, getVarExonNumberSNS,
                                                                                  getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                                                  isCIDomainInRegion,
                                                                                  isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                                  getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                  getClosestSpliceSiteScores,
                                                                                  varInSpliceRegion, getPriorProbRefSpliceDonorSNS):
        '''
        Tests function for in-frame FICTIONAL variant that does not disrupt CI domain where altZScore > refZScore and 6.2 <= altMES <= 8.5 
        and altZScore > closestZScore (in this case variant is in a ref splice donor so altZScore > closestAltZScore) so possible splice rescue
        '''
        # this example is NOT based on a real variant
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["NA"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 1)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 1)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon22")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 8)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {"altMaxEntScanScore": 8.75,
                                                                                       "refMaxEntScanScore": 5.07,
                                                                                       "altZScore": 0.34860910053737093,
                                                                                       "refZScore": -1.2314711132967735})
    def test_getPriorProbSpliceRescueNonsenseSNSAltGreaterRefHighMES(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                                    varInExonicPortion, isSplicingWindowInFrame, getVarStrand,
                                                                    getVarExonNumberSNS, getSpliceAcceptorBoundaries, getVarWindowPosition,
                                                                    isCIDomainInRegion, isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS):
        '''
        Tests function for in-frame FICTIONAL variant that: 
        does not disrupt CI domain and altZScore > refZScore and altMES > 8.5 so possible splice rescue
        '''
        # this example is NOT based on a real variant
        boundaries = "enigma"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["NA"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 1)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 1)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 0)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon3")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 6)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    def test_getPriorProbSpliceRescueNonsenseSNSBRCA1MissingExon4(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                                  varInExonicPortion, isSplicingWindowInFrame,
                                                                  getVarStrand, getVarExonNumberSNS, getSpliceAcceptorBoundaries,
                                                                  getVarWindowPosition, isCIDomainInRegion,
                                                                  isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Tests that function works correctly for exons in BRCA1 exon 3 (because BRCA1 exon 4 does not exist in numbering)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.89T>A"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 1)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon9")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 5)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTCTTAAGA',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -10.62,
                                                                                       'altMaxEntScanScore': -2.97,
                                                                                       'refSeq': 'TTCTGAAGA',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -4.68360288482572,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -7.9682805032581125})
    def test_getPriorProbSpliceRescueNonsenseSNSBRCA1CappedPriorExon9(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                                      varInExonicPortion, isSplicingWindowInFrame,
                                                                      getVarStrand, getVarExonNumberSNS, getSpliceAcceptorBoundaries,
                                                                      getVarWindowPosition, isCIDomainInRegion,
                                                                      isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                      getMaxMaxEntScanScoreSlidingWindowSNS):
        '''Tests that function works correctly for nonsense variant in BRCA1 exon 9 (capped prior due to inframe exon skipping)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.562G>T"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["capped"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon10")
    def test_getPriorProbSpliceRescueNonsenseSNSBRCA1CappedPriorExon10(self, getVarConsequences, varInExon, varInIneligibleDeNovoExon,
                                                                       varInExonicPortion, isSplicingWindowInFrame, getVarExonNumberSNS):
        '''Tests that function works correctly for nonsense variant in BRCA1 exon 10 (capped prior due to inframe exon skipping)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.667A>T"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["capped"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], "-")
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")
        
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon12")
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [False, True])
    def test_getPriorProbSpliceRescueNonsenseSNSBRCA2CappedPriorExon12SpliceAcceptor(self, getVarConsequences, varInExon,
                                                                                     varInIneligibleDeNovoExon, varInExonicPortion,
                                                                                     isSplicingWindowInFrame, getVarExonNumberSNS,
                                                                                     varInSpliceRegion):
        '''
        Tests that function works correctly for nonsense variant in BRCA2 exon 12 splice acceptor 
        (capped prior due to inframe exon skipping)
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.6844G>T"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["capped"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 1)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], "-")
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], "-")
        self.assertEquals(spliceRescueInfo["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon12")
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 4)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CCTAAAAGG',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -11.85,
                                                                                       'altMaxEntScanScore': -11.53,
                                                                                       'refSeq': 'CCTTAAAGG',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -8.359006860483403,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.496405139947242})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbSpliceRescueNonsenseSNSBRCA2NoCappedPriorExon12(self, getVarConsequences, varInExon,
                                                                         varInIneligibleDeNovoExon, varInExonicPortion,
                                                                         isSplicingWindowInFrame, getVarStrand,
                                                                         getVarExonNumberSNS, getSpliceAcceptorBoundaries,
                                                                         getVarWindowPosition, isCIDomainInRegion,
                                                                         isDeNovoWildTypeSplicePosDistanceDivisibleByThree,
                                                                         getMaxMaxEntScanScoreSlidingWindowSNS, varInSpliceRegion):
        '''
        Tests that function works correctly for nonsense variant in BRCA2 exon 12 (not in splice acceptor/donor)
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.6911T>A"
        spliceRescueInfo = calcVarPriors.getPriorProbSpliceRescueNonsenseSNS(self.variant, boundaries, deNovoDonorInRefAcc=False)
        self.assertEquals(spliceRescueInfo["priorProb"], priorProbs["pathogenic"])
        self.assertEquals(spliceRescueInfo["enigmaClass"], enigmaClasses["class5"])
        self.assertEquals(spliceRescueInfo["spliceRescue"], 0)
        self.assertEquals(spliceRescueInfo["spliceFlag"], 0)
        self.assertEquals(spliceRescueInfo["frameshiftFlag"], 0)
        self.assertEquals(spliceRescueInfo["inExonicPortionFlag"], 0)
        self.assertEquals(spliceRescueInfo["CIDomainInRegionFlag"], 0)
        self.assertEquals(spliceRescueInfo["isDivisibleFlag"], 0)
        self.assertEquals(spliceRescueInfo["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    def test_getDeNovoSpliceFrameshiftStatusDonorBRCA1(self, isSplicingWindowInFrame, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Checks that function works for minus strand (BRCA1) variant in exon (also in reference splice site)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.303T>G"
        deNovoSpliceFrameshift = calcVarPriors.getDeNovoSpliceFrameshiftStatus(self.variant, donor=True, deNovoDonorInRefAcc=True)
        self.assertFalse(deNovoSpliceFrameshift)

    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = False)
    def test_getDeNovoSpliceFrameshiftStatusAccBRCA1(self, isSplicingWindowInFrame, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Checks that function works for minus strand (BRCA1) variant in intronic portion of reference acceptor site'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.4358-12t>G"
        deNovoSpliceFrameshift = calcVarPriors.getDeNovoSpliceFrameshiftStatus(self.variant, donor=False, deNovoDonorInRefAcc=False)
        self.assertTrue(deNovoSpliceFrameshift)

    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = False)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = False)
    def test_getDeNovoSpliceFrameshiftStatusDonorBRCA2(self, isSplicingWindowInFrame, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Checks that function works for plus strand (BRCA2) variant in intron (not in native splice site)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.7805+11c>T"
        deNovoSpliceFrameshift = calcVarPriors.getDeNovoSpliceFrameshiftStatus(self.variant, donor=True, deNovoDonorInRefAcc=False)
        self.assertTrue(deNovoSpliceFrameshift)

    @mock.patch('calcVarPriors.isSplicingWindowInFrame', return_value = True)
    @mock.patch('calcVarPriors.isDeNovoWildTypeSplicePosDistanceDivisibleByThree', return_value = True)
    def test_getDeNovoSpliceFrameshiftStatusAccBRCA2(self, isSplicingWindowInFrame, isDeNovoWildTypeSplicePosDistanceDivisibleByThree):
        '''Checks that function works for plus strand (BRCA2) variant in exonic portion of reference acceptor site'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "c.69T>G"
        deNovoSpliceFrameshift = calcVarPriors.getDeNovoSpliceFrameshiftStatus(self.variant, donor=False, deNovoDonorInRefAcc=False)
        self.assertFalse(deNovoSpliceFrameshift)

    def test_getStructuralVarFrameshiftStatusnsertionTrue(self):
        '''Tests function for variant where number of nucleotides inserted is NOT divisible by 3, which causes a frameshift'''
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "GAG"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertTrue(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusInsertionFalse(self):
        '''Tests function for variant where number of nucleotides inserted is divisible by 3, which does NOT cause a frameshift'''
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "TTTA"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertFalse(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusDeletionTrue(self):
        '''Tests function for variant where number of nucleotides deleted is NOT divisible by 3, which causes a frameshift'''
        self.variant["Ref"] = "TGAAATTTT"
        self.variant["Alt"] = "T"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertTrue(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusDeletionFalse(self):
        '''Tests function for variant where number of nucleotides deleted is divisible by 3, which does NOT cause a frameshift'''
        self.variant["Ref"] = "AAAGAAG"
        self.variant["Alt"] = "A"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertFalse(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusDelinsTrue(self):
        '''
        Tests function for variant where:
          number of nucleotides deleted is divisible by 3 BUT
          number of nucleotides inserted is NOT divisible by 3, which causes a frameshift
        '''
        self.variant["Ref"] = "AAG"
        self.variant["Alt"] = "TAAGACT"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertTrue(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusDelinsFalseUnequal(self):
        '''
        Tests function for variant where:
          number of nucleotides deleted is divisible by 3 AND
          number of nucleotides inserted is divisible by 3, which does NOT cause a frameshift
        '''
        self.variant["Ref"] = "AATACA"
        self.variant["Alt"] = "CTGATGGTG"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertFalse(structuralVarFrameshift)

    def test_getStructuralVarFrameshiftStatusDelinsFalseEqual(self):
        '''
        Tests function for variant where:
          number of nucleotides deleted = number inserted, which does NOT cause a frameshift
        '''
        self.variant["Ref"] = "TT"
        self.variant["Alt"] = "AA"
        structuralVarFrameshift = calcVarPriors.getStructuralVarFrameshiftStatus(self.variant)
        self.assertFalse(structuralVarFrameshift)
        
    def test_getEnigmaClass(self):
        ''''
        Tests that predicted qualititative ENIGMA class is assigned correctly based on prior prob
        Specifically tests for priors in class 1 and class 5
        and most commonly assigned priorProb = 0.04, 0.34, and 0.97
        '''
        priorProb = 0.0001
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class1"])
        
        priorProb = 0.04
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class2"])

        priorProb = 0.34
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class3"])

        priorProb = 0.97
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class4"])
                
        priorProb = 0.995
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, enigmaClasses["class5"])

        priorProb = "N/A"
        enigmaClass = calcVarPriors.getEnigmaClass(priorProb)
        self.assertEquals(enigmaClass, None)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon14',
                                                                          'donorStart': 43076490,
                                                                          'donorEnd': 43076482})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 9.21,
                                                                               "zScore": 0.5461191272666394}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceDonorSNSLowProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                       getVarSpliceRegionBounds, getRefAltScores,
                                                       getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that creates a resaonble splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that creates a reasonable splice donor site
        self.variant["Pos"] = "43076489"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon14',
                                                                          'donorStart': 43076490,
                                                                          'donorEnd': 43076482})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 6.12,
                                                                               "zScore": -0.7806330088060529}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 5)
    def test_getPriorProbRefSpliceDonorSNSModerateProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that weakens a reasonably strong splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that weakens a reasonably strong splice donor site
        self.variant["Pos"] = "43076485"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 5)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TTTTACCAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon7',
                                                                          'donorStart': 43104124,
                                                                          'donorEnd': 43104116})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 3.23,
                                                                               "zScore": -2.021511220213846},
                                                                 "altScores": {"maxEntScanScore": -4.42,
                                                                               "zScore": -5.306188838646238}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 4)
    def test_getPriorProbRefSpliceDonorSNSHighProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                        getVarSpliceRegionBounds, getRefAltScores,
                                                        getVarSeqIndexSNS):
        '''Tests fucntion for BRCA1 variant that further weakens a weak splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that further weakens a weak splice donor site
        self.variant["Pos"] = "43104120"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 4)
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTTACCTT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon14',
                                                                          'donorStart': 43076490,
                                                                          'donorEnd': 43076482})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.57,
                                                                               "zScore": 1.1300618149879533},
                                                                 "altScores": {"maxEntScanScore": 10.77,
                                                                               "zScore": 1.2159357396528523}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 0)
    def test_getPriorProbRefSpliceDonorSNSImprovedProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that makes a splice donor site stronger or equally strong
        self.variant["Pos"] = "43076490"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 0)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ACTCACCTG")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon9',
                                                                          'donorStart': 43097246,
                                                                          'donorEnd': 43097238})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -2.3392447414739723,
                                                                               'maxEntScanScore': 2.49},
                                                                 'refScores': {'zScore': 1.1729987773204027,
                                                                               'maxEntScanScore': 10.67}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 3)
    def test_getPriorProbRefSpliceDonorSNSCappedProbBRCA1Exon9(self, getFastaSeq, getVarType, getVarLocation,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant in exon 9 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant in exon 9 that has a capped prior probability
        self.variant["Pos"] = "43097243"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 3)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATTACCCT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon10',
                                                                          'donorStart': 43095848,
                                                                          'donorEnd': 43095840})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -3.7604581946780535,
                                                                               'maxEntScanScore': -0.82},
                                                                 'refScores': {'zScore': -0.8407447560714822,
                                                                               'maxEntScanScore': 5.98}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 2)
    def test_getPriorProbRefSpliceDonorSNSCappedProbBRCA1Exon10(self, getFastaSeq, getVarType, getVarLocation,
                                                                getVarSpliceRegionBounds, getRefAltScores,
                                                                getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant in exon 10 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant in exon 10 that has a capped prior probability
        self.variant["Pos"] = "43095846"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 2)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon13',
                                                                          'donorStart': 32346894,
                                                                          'donorEnd': 32346902})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 8.91,
                                                                               "zScore": 0.4173082402692903}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceDonorSNSLowProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                       getVarSpliceRegionBounds, getRefAltScores,
                                                       getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that creates a resaonble splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that creates a reasonable splice donor site
        self.variant["Pos"] = "32346895"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon13',
                                                                          'donorStart': 32346894,
                                                                          'donorEnd': 32346902})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 4.35,
                                                                               "zScore": -1.5406172420904107}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 5)
    def test_getPriorProbRefSpliceDonorSNSModerateProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that weakens a reasonably strong splice donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that weakens a reasonably strong splice donor site
        self.variant["Pos"] = "32346899"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 5)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CAGGCAAGT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon17',
                                                                          'donorStart': 32362691,
                                                                          'donorEnd': 32362699})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 3.1,
                                                                               "zScore": -2.07732927124603},
                                                                 "altScores": {"maxEntScanScore": 0.56,
                                                                               "zScore": -3.1679281144902496}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 2)
    def test_getPriorProbRefSpliceDonorSNSHighProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                        getVarSpliceRegionBounds, getRefAltScores,
                                                        getVarSeqIndexSNS):
        '''Tests fucntion for BRCA2 variant that further weakens a weak splice donor site'''  
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that further weakens a weak splice donor site
        self.variant["Pos"] = "32362693"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 2)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCGGTAAGA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon13',
                                                                          'donorStart': 32346894,
                                                                          'donorEnd': 32346902})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.53,
                                                                               "zScore": 1.1128870300549731},
                                                                 "altScores": {"maxEntScanScore": 11.78,
                                                                               "zScore": 1.649599059210593}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 8)
    def test_getPriorProbRefSpliceDonorSNSImprovedProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                            getVarSpliceRegionBounds, getRefAltScores,
                                                            getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that makes a splice donor site stronger or equally strong
        self.variant["Pos"] = "32346902"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 8)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ATGGTAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_donor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon12',
                                                                          'donorStart': 32344651,
                                                                          'donorEnd': 32344659})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -2.021511220213846,
                                                                               'maxEntScanScore': 3.23},
                                                                 'refScores': {'zScore': -1.3516946078276324,
                                                                               'maxEntScanScore': 4.79}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 0)
    def test_getPriorProbRefSpliceDonorSNSCappedProbBRCA2Exon12(self, getFastaSeq, getVarType, getVarLocation,
                                                                getVarSpliceRegionBounds, getRefAltScores,
                                                                getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant in exon 12 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant in exon 12 that has a capped prior probability
        self.variant["Pos"] = "32344651"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceDonorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 0)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43104281,
                                                                          'exonName': 'exon7',
                                                                          'acceptorEnd': 43104259})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 10.94,
                                                                               "zScore": 1.214256756422072}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 6)    
    def test_getPriorProbRefSpliceAcceptorSNSLowProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                          getVarSpliceRegionBounds, getRefAltScores,
                                                          getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that creates a resaonble splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that creates a reasonable splice acceptor site
        self.variant["Pos"] = "43104275"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 6)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43104281,
                                                                          'exonName': 'exon7',
                                                                          'acceptorEnd': 43104259})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 9.01,
                                                                               "zScore": 0.4212132894055031}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 14)
    def test_getPriorProbRefSpliceAcceptorSNSModerateProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that weakens a reasonably strong splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that weakens a reasonably strong splice acceptor site
        self.variant["Pos"] = "43104267"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 14)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "GAACTTTAACACATTAGAAAAAC")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43124135,
                                                                          'exonName': 'exon2',
                                                                          'acceptorEnd': 43124113})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 4.9,
                                                                               "zScore":  -1.2675994823240817},
                                                                 "altScores": {"maxEntScanScore": -3.17,
                                                                               "zScore": -4.583589523165384}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 19)
    def test_getPriorProbRefSpliceAcceptorSNSHighProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                           getVarSpliceRegionBounds, getRefAltScores,
                                                           getVarSeqIndexSNS):
        '''Tests fucntion for BRCA1 variant that further weakens a weak splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant that further weakens a weak splice acceptor site
        self.variant["Pos"] = "43124116"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 19)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "CATCTGTAAAATACAAGGGAAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43104281,
                                                                          'exonName': 'exon7',
                                                                          'acceptorEnd': 43104259})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 11.68,
                                                                               "zScore": 1.5183252360035546},
                                                                 "altScores": {"maxEntScanScore": 12.41,
                                                                               "zScore": 1.8182846820771794}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 20)
    def test_getPriorProbRefSpliceAcceptorSNSImprovedProbBRCA1(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA1 variants that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
    
        # checks prior prob for BRCA1 variant that makes a splice acceptor site stronger or equally strong
        self.variant["Pos"] = "43104261"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 20)
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ATCCTAAAAAATTTCCCCCCAAA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43097309,
                                                                          'exonName': 'exon9',
                                                                          'acceptorEnd': 43097287})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -2.6769979755193316,
                                                                               'maxEntScanScore': 1.47},
                                                                 'refScores': {'zScore': -2.122278451958519,
                                                                               'maxEntScanScore': 2.82}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 21)
    def test_getPriorProbRefSpliceAcceptorSNSCappedProbBRCA1Exon9(self, getFastaSeq, getVarType, getVarLocation,
                                                                  getVarSpliceRegionBounds, getRefAltScores,
                                                                  getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant in exon 9 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant in exon 9 that has a capped prior probability
        self.variant["Pos"] = "43097288"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 21)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "ACACTATAGGGAAAAGACAGAGT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43095942,
                                                                          'exonName': 'exon10',
                                                                          'acceptorEnd': 43095920})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -2.607144405885748,
                                                                               'maxEntScanScore': 1.64},
                                                                 'refScores': {'zScore': 0.8280076066834324,
                                                                               'maxEntScanScore': 10.0}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 18)
    def test_getPriorProbRefSpliceAcceptorSNSCappedProbBRCA1Exon10(self, getFastaSeq, getVarType, getVarLocation,
                                                                   getVarSpliceRegionBounds, getRefAltScores,
                                                                   getVarSeqIndexSNS):
        '''Tests function for BRCA1 variant in exon 10 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"

        # checks prior prob for BRCA1 variant in exon 10 that has a capped prior probability
        self.variant["Pos"] = "43095924"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 18)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32379730,
                                                                          'exonName': 'exon23',
                                                                          'acceptorEnd': 32379752})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 10.09,
                                                                               "zScore": 0.8649889082541532}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 21)
    def test_getPriorProbRefSpliceAcceptorSNSLowProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                          getVarSpliceRegionBounds, getRefAltScores,
                                                          getVarSeqIndex):
        '''Tests function for BRCA2 variant that creates a resaonble splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that creates a reasonable splice acceptor site
        self.variant["Pos"] = "32379751"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 21)   

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32379730,
                                                                          'exonName': 'exon23',
                                                                          'acceptorEnd': 32379752})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 8.84,
                                                                               "zScore": 0.3513597197719193}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 16)
    def test_getPriorProbRefSpliceAcceptorSNSModerateProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                               getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that weakens a reasonably strong splice acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that weakens a reasonably strong splice acceptor site
        self.variant["Pos"] = "32379746"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["moderate"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 16)        

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "AAGTATTTATTCTTTGATAGATT")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32356408,
                                                                          'exonName': 'exon15',
                                                                          'acceptorEnd': 32356430})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 5.16,
                                                                               "zScore": -1.1607646111197771},
                                                                 "altScores": {"maxEntScanScore": -2.91,
                                                                               "zScore": -4.4767546519610795}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 19)
    def test_getPriorProbRefSpliceAcceptorSNSHighProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                           getVarSpliceRegionBounds, getRefAltScores,
                                                           getVarSeqIndexSNS):
        '''Tests fucntion for BRCA2 variant that further weakens a weak splice acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that further weakens a weak splice acceptor site
        self.variant["Pos"] = "32356427"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["high"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class4"])
        self.assertEquals(priorProb["varStart"], 19)        
        
    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TCTCATCTTTCTCCAAACAGTTA")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32379730,
                                                                          'exonName': 'exon23',
                                                                          'acceptorEnd': 32379752})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {"refScores": {"maxEntScanScore": 10.35,
                                                                               "zScore": 0.9718237794584578},
                                                                 "altScores": {"maxEntScanScore": 10.42,
                                                                               "zScore": 1.000587014013463}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 1)
    def test_getPriorProbRefSpliceAcceptorSNSImprovedProbBRCA2(self, getFastaSeq, getVarType, getVarLocationSNS,
                                                                getVarSpliceRegionBounds, getRefAltScores,
                                                               getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant that makes a splice site stronger or equally strong'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant that makes a splice acceptor site stronger or equally strong
        self.variant["Pos"] = "32379731"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["low"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["varStart"], 1)

    @mock.patch('calcVarPriors.getFastaSeq', return_value = "TATGAAATATTTCTTTTTAGGAG")
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocation', return_value = "splice_acceptor_variant")
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32344538,
                                                                          'exonName': 'exon12',
                                                                          'acceptorEnd': 32344560})
    @mock.patch('calcVarPriors.getRefAltScores', return_value = {'altScores': {'zScore': -2.594817305362174,
                                                                               'maxEntScanScore': 1.67},
                                                                 'refScores': {'zScore': 0.10070867579258944,
                                                                               'maxEntScanScore': 8.23}})
    @mock.patch('calcVarPriors.getVarSeqIndexSNS', return_value = 9)
    def test_getPriorProbRefSpliceAcceptorSNSCappedProbBRCA2Exon12(self, getFastaSeq, getVarType, getVarLocation,
                                                                   getVarSpliceRegionBounds, getRefAltScores,
                                                                   getVarSeqIndexSNS):
        '''Tests function for BRCA2 variant in exon 12 that has a capped prior probability'''
        boundaries = "engima"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"

        # checks prior prob for BRCA2 variant in exon 12 that has a capped prior probability
        self.variant["Pos"] = "32344547"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbRefSpliceAcceptorSNS(self.variant, boundaries)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["varStart"], 9)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["afterGreyZone"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbAfterGreyZoneMissenseSNS(self, getVarType, getVarLocationSNS, getVarConsequences):
        '''
        Tests that:
        prior prob is set to N/A and ENIGMA class is class 2 for a BRCA2 missense variant after the grey zone
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32398528"
        self.variant["Hg38_End"] = "32398528"

        self.variant["Pos"] = "32398528"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbAfterGreyZoneSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["afterGreyZone"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    def test_getPriorProbAfterGreyZoneNonesenseSNS(self, getVarType, getVarLocationSNS, getVarConsequences):
        '''
        Tests that:
        prior prob is set to N/A and ENIGMA class is class 2 for a BRCA2 nonsense variant after the grey zone
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["Hg38_Start"] = "32398492"
        self.variant["Hg38_End"] = "32398492"

        self.variant["Pos"] = "32398492"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbAfterGreyZoneSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon24")
    def test_varInIneligibleDeNovoExonDonorBRCA1True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in last exon of BRCA1 is correctly identified as ineligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    def test_varInIneligibleDeNovoExonDonorBRCA1False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA1 is correctly identified as eligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertFalse(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon27")
    def test_varInIneligibleDeNovoExonDonorBRCA2True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in last exon of BRCA2 is correctly identified as ineligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon19")
    def test_varInIneligibleDeNovoExonDonorBRCA2False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA2 is correctly identified as eligible for de novo donor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=True)
        self.assertFalse(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon1")
    def test_varInIneligibleDeNovoExonAccBRCA1True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in first exon of BRCA1 is correctly identified as ineligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon16")
    def test_varInIneligibleDeNovoExonAccBRCA1False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA1 is correctly identified as eligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA1"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertFalse(ineligibleDeNovo)
        
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon1")
    def test_varInIneligibleDeNovoExonAccBRCA2True(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in first exon of BRCA2 is correctly identified as ineligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertTrue(ineligibleDeNovo)

    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon2")
    def test_varInIneligibleDeNovoExonAccBRCA2False(self, varInExon, getVarExonNumberSNS):
        '''Tests that variant in other exon of BRCA2 is correctly identified as eligible for de novo acceptor'''
        self.variant["Gene_Symbol"] = "BRCA2"
        ineligibleDeNovo = calcVarPriors.varInIneligibleDeNovoExon(self.variant, donor=False)
        self.assertFalse(ineligibleDeNovo)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusWithFramsehiftDonor(self, getDeNovoSpliceFrameshiftStatus):
        '''Tests that function returns false if variant causes a frameshift for de novo donor'''
        boundaries = "enigma"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusWithFramsehiftAcc(self, getDeNovoSpliceFrameshiftStatus):
        '''Tests that function returns false if variant causes a frameshift for de novo acceptor'''
        boundaries = "enigma"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=False,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)
        
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon14")
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 8)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43076575)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    def test_getDeNovoFrameshiftAndCIStatusExonDonorTrue(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                         getVarExonNumberSNS, getVarWindowPosition,
                                                         varInExonicPortionn, getVarStrand, getNewSplicePosition,
                                                         getSpliceAcceptorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo donor IS in frame and does NOT disrupt a CI domain'''
        # variant is located in exon
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43076570"
        self.variant["HGVS_cDNA"] = "c.4402A>G"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertTrue(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon15")
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 3)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = True)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32356591)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusExonDonorFalse(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                          getVarExonNumberSNS, getVarWindowPosition,
                                                          varInExonicPortion, getVarStrand, getNewSplicePosition,
                                                          getSpliceAcceptorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo acceptor IS in frame and does disrupt a CI domain'''
        # variant is located in exon
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32356591"
        self.variant["HGVS_cDNA"] = "c.7599T>G"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon8")
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 16)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32329454)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    def test_getDeNovoFrameshiftAndCIStatusExonAccTrue(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                       getVarExonNumberSNS, getVarWindowPosition,
                                                       varInExonicPortion, getVarStrand, getNewSplicePosition,
                                                       getRefSpliceDonorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo acceptor IS in frame and does NOT disrupt a CI domain'''
        # variant is located in exon
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32329450"
        self.variant["HGVS_cDNA"] = "c.639T>C"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=False,
                                                                          deNovoDonorInRefAcc=False)
        self.assertTrue(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getVarExonNumberSNS', return_value = "exon5")
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 19)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43106528)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusExonAccFalse(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                        getVarExonNumberSNS, getVarWindowPosition,
                                                        varInExonicPortion, getVarStrand, getNewSplicePosition,
                                                        getRefSpliceDonorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns False when variant de novo acceptor IS in frame and does disrupt a CI domain'''
        # variant is located in exon
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43106529"
        self.variant["HGVS_cDNA"] = "c.139T>A"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=False,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    # variant is in exonic portion of splice site, but testing to make sure it works for splice region
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon6',
                                                                          'donorStart': 32326280,
                                                                          'donorEnd': 32326288})
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 8)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326276)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca2RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    def test_getDeNovoFrameshiftAndCIStatusRefSpliceDonorTrue(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                              varInSpliceRegion, getVarSpliceRegionBounds,
                                                              getVarWindowPosition, varInExonicPortion, getVarStrand,
                                                              getNewSplicePosition, getSpliceAcceptorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo donor IS in frame and does NOT disrupt a CI domain'''
        # variant is located in reference splice donor site
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32326281"
        self.variant["HGVS_cDNA"] = "c.515A>T"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertTrue(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    # variant is in exonic portion of splice site, but testing to make sure it works for splice region
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'exonName': 'exon3',
                                                                          'donorStart': 43115728,
                                                                          'donorEnd': 43115720})
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 5)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43115729)
    @mock.patch('calcVarPriors.getSpliceAcceptorBoundaries', return_value = brca1RefSpliceAcceptorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusRefSpliceDonorFalse(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                               varInSpliceRegion, getVarSpliceRegionBounds,
                                                               getVarWindowPosition, varInExonicPortion, getVarStrand,
                                                               getNewSplicePosition, getSpliceAcceptorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns False when variant de novo donor IS in frame and does disrupt a CI domain'''
        # variant is located in reference splice donor site
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43115727"
        self.variant["HGVS_cDNA"] = "c.133A>T"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 43071258,
                                                                          'exonName': 'exon16',
                                                                          'acceptorEnd': 43071236})
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 20)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43071248)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca1RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = False)
    def test_getDeNovoFrameshiftAndCIStatusRefSpliceAccTrue(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                            varInSpliceRegion, getVarSpliceRegionBounds,
                                                            getVarWindowPosition, varInExonicPortion, getVarStrand,
                                                            getNewSplicePosition, getRefSpliceDonorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo acceptor IS in frame and does NOT disrupt a CI domain'''
        # variant is located in reference splice acceptor site
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43071248"
        self.variant["HGVS_cDNA"] = "c.4676-10t>G"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=False,
                                                                          deNovoDonorInRefAcc=False)
        self.assertTrue(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarSpliceRegionBounds', return_value = {'acceptorStart': 32370936,
                                                                          'exonName': 'exon20',
                                                                          'acceptorEnd': 32370958})
    @mock.patch('calcVarPriors.getVarWindowPosition', return_value = 16)
    @mock.patch('calcVarPriors.varInExonicPortion', return_value = False)
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32370958)
    @mock.patch('calcVarPriors.getRefSpliceDonorBoundaries', return_value = brca2RefSpliceDonorBounds)
    @mock.patch('calcVarPriors.isCIDomainInRegion', return_value = True)
    def test_getDeNovoFrameshiftAndCIStatusRefSpliceAccFalse(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                             varInSpliceRegion, getVarSpliceRegionBounds,
                                                             getVarWindowPosition, varInExonicPortion, getVarStrand,
                                                             getNewSplicePosition, getRefSpliceDonorBoundaries, isCIDomainInRegion):
        '''Tests that funciton returns True when variant de novo acceptor IS in frame and does disrupt a CI domain'''
        # variant is located in reference splice acceptor site
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Pos"] = "32370954"
        self.variant["HGVS_cDNA"] = "c.8488-2a>C"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=False,
                                                                          deNovoDonorInRefAcc=False)
        self.assertFalse(frameshiftCIStatus)

    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getDeNovoFrameshiftAndCIStatusIntronDonorTrue(self, getDeNovoSpliceFrameshiftStatus, varInExon,
                                                           varInSpliceRegion):
        '''Tests that funciton returns True when variant de novo donor IS in frame and is located in an intron'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Pos"] = "43115719"
        self.variant["HGVS_cDNA"] = "c.134+7t>G"
        frameshiftCIStatus = calcVarPriors.getDeNovoFrameshiftAndCIStatus(self.variant, boundaries, donor=True,
                                                                          deNovoDonorInRefAcc=False)
        self.assertTrue(frameshiftCIStatus)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbDeNovoDonorSNSELastExonBRCA1(self, getVarType, varInExon, varInSpliceRegion,
                                                      varInIneligibleDeNovoExon):
        '''Tests that variant in last exon of BRCA1 is correctly assigned de novo prob'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Pos"] = "43045765"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = True)
    def test_getPriorProbDeNovoDonorSNSELastExonBRCA2(self, getVarType, varInExon, varInSpliceRegion,
                                                      varInIneligibleDeNovoExon):
        '''Tests that variant in last exon of BRCA2 is correclty assigned de novo prob'''
        boundaries = "enigma"
        # the below is not the correct format for genome and transcript
        genome = "hg38"
        transcript = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Pos"] = "32398180"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGGATACCG',
                                                                                       'varWindowPosition': 2,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 1.49,
                                                                                       'altMaxEntScanScore': -3.56,
                                                                                       'refSeq': 'AAGATACCG',
                                                                                       'varStart': 1,
                                                                                       'altZScore': -4.936930962587172,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.7686143647984682})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097271)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1729987773204027,
                                                                            'sequence': 'CAGGTGAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43097243,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon9',
                                                                            'maxEntScanScore': 10.67})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['566', '593+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43097271', 'c.566', 'g.43097243', 'c.593+1'])
    def test_getPriorProbDeNovoDonorSNSExonRefGreaterAltBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                              convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA1 variant in exon where ref zscore is greater than alt zscore'''
        boundaries = "enigma"
        # the below is not the correct format for genome and transcript
        genome = "hg38"
        transcript = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.564A>G"
        self.variant["Pos"] = "43097273"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TGGTAAAAA',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -12.18,
                                                                                       'altMaxEntScanScore': -13.41,
                                                                                       'refSeq': 'AGGTAAAAA',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -9.166221752333454,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.638097115644324})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43090942)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.27990996080545155,
                                                                            'sequence': 'CAGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43090943,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon12',
                                                                            'maxEntScanScore': 8.59})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 8.59,
                                                                               'altZScore': -1.3559883040608771,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 1,
                                                                               'refZScore': 0.27990996080545155,
                                                                               'altMaxEntScanScore': 4.78,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'CTGGTAAAA',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAGGTAAAA'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['4185+2', '4185+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43090942', 'c.4185+2', 'g.43090943', 'c.4185+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteRefGreaterAltBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                    getClosestSpliceSiteScores, getPriorProbRefSpliceDonorSNS,
                                                                    getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                                    formatSplicePosition):
        '''Tests BRCA1 variant in splice site where ref zscore is greater than alt zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4184A>T"
        self.variant["Pos"] = "43090945"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGAGACT',
                                                                                       'varWindowPosition': 6,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.85,
                                                                                       'altMaxEntScanScore': -7.01,
                                                                                       'refSeq': 'AAAGAAACT',
                                                                                       'varStart': 5,
                                                                                       'altZScore': -6.418256163056683,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.061448153351276})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32344576)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.3516946078276324,
                                                                            'sequence': 'ATGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32344654,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon12',
                                                                            'maxEntScanScore': 4.79})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['6860', '6937+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32344576', 'c.6860', 'g.32344654', 'c.6937+1'])
    def test_getPriorProbDeNovoDonorSNSExonRefGreaterAltBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                              convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA2 variant in exon where ref zscore is greater than alt zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.6862A>G"
        self.variant["Pos"] = "32344578"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TGGTAAGAC',
                                                                                       'varWindowPosition': 1,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': -14.69,
                                                                                       'altMaxEntScanScore': -17.11,
                                                                                       'refSeq': 'CGGTAAGAC',
                                                                                       'varStart': 0,
                                                                                       'altZScore': -10.75488935863409,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -9.71581487018881})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32346898)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1128870300549731,
                                                                            'sequence': 'TCGGTAAGA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32346897,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon13',
                                                                            'maxEntScanScore': 10.53})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.53,
                                                                               'altZScore': 0.39154606286982035,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 1,
                                                                               'refZScore': 1.1128870300549731,
                                                                               'altMaxEntScanScore': 8.85,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'TTGGTAAGA',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'TCGGTAAGA'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['7007+2', '7007+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32346898', 'c.7007+2', 'g.32346897', 'c.7007+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteRefGreaterAltBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                    getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                    getClosestSpliceSiteScores, getPriorProbRefSpliceDonorSNS,
                                                                    getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                                    formatSplicePosition):
        '''Tests BRCA2 variant in splice site where ref zscore is greater than alt zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7006C>T"
        self.variant["Pos"] = "32346895"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGCCATT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -5.67,
                                                                                       'altMaxEntScanScore': -3.44,
                                                                                       'refSeq': 'AAGGCCTTT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -4.885406607788233,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.842900867801858})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43076560)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1300618149879533,
                                                                            'sequence': 'AAGGTAAGA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43076487,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon14',
                                                                            'maxEntScanScore': 10.57})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['4412', '4484+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43076560', 'c.4412', 'g.43076487', 'c.4484+1'])
    def test_getPriorProbDeNovoDonorSNSExonLowProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                        getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                        convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA1 variant in exon with expected low (0.02) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4415T>A"
        self.variant["Pos"] = "43076557"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATTGCACGT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -4.41,
                                                                                       'altMaxEntScanScore': -2.12,
                                                                                       'refSeq': 'ATTGCAGGT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -4.318638704999898,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -5.301895142412993})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097247)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1729987773204027,
                                                                            'sequence': 'CAGGTGAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43097243,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon9',
                                                                            'maxEntScanScore': 10.67})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.67,
                                                                               'altZScore': 0.5847623933658439,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 1.1729987773204027,
                                                                               'altMaxEntScanScore': 9.3,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'CACGTGAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAGGTGAGT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['590', '593+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43097247', 'c.590', 'g.43097243', 'c.593+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteLowProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores, getPriorProbRefSpliceDonorSNS,
                                                              getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                              formatSplicePosition):
        '''Tests BRCA1 variant in splice site with expected low (0.02) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.593G>C"
        self.variant["Pos"] = "43097244"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CTGTTGTGC',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -12.7,
                                                                                       'altMaxEntScanScore': -5.05,
                                                                                       'refSeq': 'CTGTTGTTC',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -5.57669170134067,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -8.861369319773063})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326106)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.6534615330977633,
                                                                            'sequence': 'CAGGTATGA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32326151,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon5',
                                                                            'maxEntScanScore': 9.46})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['431', '475+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32326106', 'c.431', 'g.32326151', 'c.475+1'])
    def test_getPriorProbDeNovoDonorSNSExonLowProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                        getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                        getDeNovoFrameshiftAndCIStatus, convertGenomicPosToTranscriptPos,
                                                        formatSplicePosition):
        '''Tests BRCA2 variant in exon with expected low (0.02) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.435T>G"
        self.variant["Pos"] = "32326110"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGCTTCTT',
                                                                                       'varWindowPosition': 9,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -6.24,
                                                                                       'altMaxEntScanScore': -4.4,
                                                                                       'refSeq': 'AAGCTTCTG',
                                                                                       'varStart': 8,
                                                                                       'altZScore': -5.297601446179749,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.087641553096821})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32397039)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.164411384853913,
                                                                            'sequence': 'CTGGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32397045,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon26',
                                                                            'maxEntScanScore': 10.65})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.65,
                                                                               'altZScore': 0.026581883043999093,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 1.164411384853913,
                                                                               'altMaxEntScanScore': 8.0,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'CTTGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CTGGTAAGT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['9643', '9648+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32397039', 'c.9643', 'g.32397045', 'c.9648+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteLowProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores,getPriorProbRefSpliceDonorSNS,
                                                              getDeNovoSpliceFrameshiftStatus, getDeNovoFrameshiftAndCIStatus,
                                                              convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA2 variant in splice site with expected low (0.02) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9648G>T"
        self.variant["Pos"] = "32397044"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AGTGTGAGC',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -2.47,
                                                                                       'altMaxEntScanScore': 3.73,
                                                                                       'refSeq': 'AGTGTGACC',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -1.8068264085515982,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.468918073163471})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43115744)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9196706995589503,
                                                                            'sequence': 'CAAGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43115725,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon3',
                                                                            'maxEntScanScore': 10.08})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['116', '134+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43115744', 'c.116', 'g.43115725', 'c.134+1'])
    def test_getPriorProbDeNovoDonorSNSExonModProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                        getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                        convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA1 variant in exon with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.120C>G"
        self.variant["Pos"] = "43115740"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTTGTAAGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.35,
                                                                                       'altMaxEntScanScore': 7.4,
                                                                                       'refSeq': 'TTTGCAAGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.2310398909506982,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.558654471715541})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43115729)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9196706995589503,
                                                                            'sequence': 'CAAGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43115725,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon3',
                                                                            'maxEntScanScore': 10.08})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.08,
                                                                               'altZScore': 0.05663775667671392,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 0,
                                                                               'refZScore': 0.9196706995589503,
                                                                               'altMaxEntScanScore': 8.07,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'TAAGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAAGTAAGT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['131', '134+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43115729', 'c.131', 'g.43115725', 'c.134+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteModProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores, getPriorProbRefSpliceDonorSNS,
                                                              getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                              formatSplicePosition):
        '''Tests BRCA1 variant in splice site with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.132C>T"
        self.variant["Pos"] = "43115728"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCAGTATGT',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.5,
                                                                                       'altMaxEntScanScore': 5.0,
                                                                                       'refSeq': 'TCATTATGT',
                                                                                       'varStart': 3,
                                                                                       'altZScore': -1.2615269869294883,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.911168785187702})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32332406)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.09528102277591848,
                                                                            'sequence': 'CAGGTACCT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32333388,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon10',
                                                                            'maxEntScanScore': 8.16})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['928', '1909+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32332406', 'c.928', 'g.32333388', 'c.1909+1'])
    def test_getPriorProbDeNovoDonorSNSExonModProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                        getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                        getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                        convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA2 variant in exon with expected moderate (0.3) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.928T>G"
        self.variant["Pos"] = "32332406"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTAGTGAGT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -1.35,
                                                                                       'altMaxEntScanScore': 5.79,
                                                                                       'refSeq': 'TTAGTGGGT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -0.9223249845031366,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.9880240950400365})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32341193)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.9883698392908697,
                                                                            'sequence': 'TGGGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32341197,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon11',
                                                                            'maxEntScanScore': 10.24})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.24,
                                                                               'altZScore': 0.37866497417008577,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 0.9883698392908697,
                                                                               'altMaxEntScanScore': 8.82,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'TGAGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'TGGGTAAGT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['6838', '6841+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32341193', 'c.6838', 'g.32341197', 'c.6841+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteModProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                              getClosestSpliceSiteScores, getPriorProbRefSpliceDonorSNS,
                                                              getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                              formatSplicePosition):
        '''Tests BRCA2 variant in splice site with expected moderate prob (0.3) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.6841G>A"
        self.variant["Pos"] = "32341196"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ACGGTGAGA',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 2.78,
                                                                                       'altMaxEntScanScore': 8.94,
                                                                                       'refSeq': 'ACTGTGAGA',
                                                                                       'varStart': 2,
                                                                                       'altZScore': 0.4301893289690249,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.2147275507098687})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43099838)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.49030107623445457,
                                                                            'sequence': 'TGGGTAAGG',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43099774,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon8',
                                                                            'maxEntScanScore': 9.08})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['484', '547+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43099838', 'c.484', 'g.43099774', 'c.547+1'])
    def test_getPriorProbDeNovoDonorSNSExonHighProbBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                         getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                         getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                         convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA1 variant in exon with expected high (0.64) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.483T>G"
        self.variant["Pos"] = "43099839"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTATGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 2.14,
                                                                                       'altMaxEntScanScore': 9.79,
                                                                                       'refSeq': 'AAGGGATGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': 0.7951535087948461,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.4895241096375464})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32379454)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.2545790057520567,
                                                                            'sequence': 'CAGGTAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32379516,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon22',
                                                                            'maxEntScanScore': 10.86})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['8892', '8953+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32379454', 'c.8892', 'g.32379516', 'c.8953+1'])
    def test_getPriorProbDeNovoDonorSNSExonHighProbBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                         getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                         getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                         convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA2 variant in exon with expected high (0.64) prior prob where alt zscore > ref zscore'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8893G>T"
        self.variant["Pos"] = "32379455"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AATGTATGG',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.77,
                                                                                       'altMaxEntScanScore': 3.37,
                                                                                       'refSeq': 'AAAGTATGG',
                                                                                       'varStart': 2,
                                                                                       'altZScore': -1.9613994729484163,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.7896516236186177})
    @mock.patch('calcVarPriors.getNewSplicePosition', retunr_value = 43104183)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.021511220213846,
                                                                            'sequence': 'TTGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43104121,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon7',
                                                                            'maxEntScanScore': 3.23})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['380', '441+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43104183', 'c.380', 'g.43104121', 'c.441+1'])
    def test_getPriorProbDeNovoDonorSNSExonLowProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                  getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                  convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA1 variant in exon with expected low (0.02) prior prob that is promoted to moderate prior prob 
        because alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.379A>T"
        self.variant["Pos"] = "43104184"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AATGTGACT',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 0.21,
                                                                                       'altMaxEntScanScore': 3.25,
                                                                                       'refSeq': 'AATGTGCCT',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -2.012923827747356,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.318207482653823})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32362624)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.07732927124603,
                                                                            'sequence': 'CAGGCAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32362694,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon17',
                                                                            'maxEntScanScore': 3.1})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['7907', '7976+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32362624', 'c.7907', 'g.32362694', 'c.7976+1'])
    def test_getPriorProbDeNovoDonorSNSExonLowProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                  getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                  convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA2 variant in exon with expected low (0.02) prior prob that is promoted to moderate prior prob 
        because alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7910C>A"
        self.variant["Pos"] = "32362627"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GAGGTATCC',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.17,
                                                                                       'altMaxEntScanScore': 7.59,
                                                                                       'refSeq': 'GAGGCATCC',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.14945966251904425,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.4813679395171317})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43094763)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.9867304280018111,
                                                                            'sequence': 'TAGGTATTG',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43091434,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon11',
                                                                            'maxEntScanScore': 5.64})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['768', '4096+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43094763', 'c.768', 'g.43091434', 'c.4096+1'])
    def test_getPriorProbDeNovoDonorSNSExonModProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                  getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                  convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA1 variant in exon with expected moderate (0.3) prior prob that is promoted to high prior prob 
        because alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Referenec_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.769C>T"
        self.variant["Pos"] = "43094762"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CAGGTGGGG',
                                                                                       'varWindowPosition': 7,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 6.34,
                                                                                       'altMaxEntScanScore': 6.92,
                                                                                       'refSeq': 'CAGGTGTGG',
                                                                                       'varStart': 6,
                                                                                       'altZScore': -0.43713731014645635,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -0.686171691674664})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32362543)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.07732927124603,
                                                                            'sequence': 'CAGGCAAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32362694,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon17',
                                                                            'maxEntScanScore': 3.1})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['7826', '7976+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32362543', 'c.7826', 'g.32362694', 'c.7976+1'])
    def test_getPriorProbDeNovoDonorSNSExonModProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                  getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                  getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                  convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA2 variant in exon with expected moderate (0.3) prior prob that is promoted to high prior prob 
        because alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Referenec_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7829T>G"
        self.variant["Pos"] = "32362546"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTATGG',
                                                                                       'varWindowPosition': 3,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.77,
                                                                                       'altMaxEntScanScore': 9.26,
                                                                                       'refSeq': 'AAAGTATGG',
                                                                                       'varStart': 2,
                                                                                       'altZScore': 0.5675876084328637,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.7896516236186177})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43104183)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -2.021511220213846,
                                                                            'sequence': 'TTGGTAAAA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43104121,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon7',
                                                                            'maxEntScanScore': 3.23})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['380', '441+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43104183', 'c.380', 'g.43104121', 'c.441+1'])
    def test_getPriorProbDeNovoDonorSNSExonHighProbGreaterSubBRCA1(self, getVarType, varInExon, varInSpliceRegion, varInIneligibleDeNovoExon,
                                                                   getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                   getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                   convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA1 variant in exon with expected high (0.64) prior prob and alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.379A>G"
        self.variant["Pos"] = "43104184"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTAATG',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 0.81,
                                                                                       'altMaxEntScanScore': 8.99,
                                                                                       'refSeq': 'AAGATAATG',
                                                                                       'varStart': 3,
                                                                                       'altZScore': 0.45165781013525,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.0605857086591257})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32363225)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.4044271515695557,
                                                                            'sequence': 'AAGGTAAAT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32363534,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon18',
                                                                            'maxEntScanScore': 8.88})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['8023', '8331+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32363225', 'c.8023', 'g.32363534', 'c.8331+1'])
    def test_getPriorProbDeNovoDonorSNSExonHighProbGreaterSubBRCA2(self, getVarType, varInExon, varInSpliceRegion,
                                                                   varInIneligibleDeNovoExon, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                   getNewSplicePosition, getClosestSpliceSiteScores,
                                                                   getDeNovoSpliceFrameshiftStatus, getDeNovoFrameshiftAndCIStatus,
                                                                   convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''
        Tests BRCA2 variant in exon with expected high (0.64) prior prob and alt zscore > subsequent z score
        '''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8023A>G"
        self.variant["Pos"] = "32363225"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    # the below variant is in exonic portion of splice site, just making sure that function works if varInExon == False
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAAGTAGGT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -0.91,
                                                                                       'altMaxEntScanScore': 6.84,
                                                                                       'refSeq': 'AAAGCAGGT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -0.47148688001241607,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -3.799101460777258})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32316524)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.17686125120757246,
                                                                            'sequence': 'CAGGTATTG',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32316528,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon2',
                                                                            'maxEntScanScore': 8.35})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 8.35,
                                                                               'altZScore': -0.9867304280018111,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 0,
                                                                               'refZScore': 0.17686125120757246,
                                                                               'altMaxEntScanScore': 5.64,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'TAGGTATTG',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAGGTATTG'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['64', '67+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32316524', 'c.64', 'g.32316528', 'c.67+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteHighProbGreaterClosestAltBRCA2(self, getVarType, varInExon, varInSpliceRegion,
                                                                                varInIneligibleDeNovoExon, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                                getNewSplicePosition, getClosestSpliceSiteScores,
                                                                                getPriorProbRefSpliceDonorSNS, getDeNovoSpliceFrameshiftStatus,
                                                                                convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests BRCA2 variant in splice site with expected high prob (0.64) prior prob where alt zscore > ref zscore and alt zscore > closestaltZ'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.65C>T"
        self.variant["Pos"] = "32316525"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 1)
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TAAGTGAGT',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -2.05,
                                                                                       'altMaxEntScanScore': 6.43,
                                                                                       'refSeq': 'TAAGTGACT',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -0.6475284255754594,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.288582831367183})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43082460)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.5573608046773153,
                                                                            'sequence': 'AAGGTGTGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43082403,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon13',
                                                                            'maxEntScanScore': 6.64})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['4301', '4357+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43082460', 'c.4301', 'g.43082403', 'c.4357+1'])
    def test_getPriorProbDeNovoDonorSNSNoFrameshiftOrCIDisruptionBRCA1(self, getVarType, varInExon, varInSpliceRegion,
                                                                       varInIneligibleDeNovoExon, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                       getNewSplicePosition, getClosestSpliceSiteScores,
                                                                       getDeNovoSpliceFrameshiftStatus, getDeNovoFrameshiftAndCIStatus,
                                                                       convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests that prior prob is changed to low prob (0.02) when de novo splicing does not cause a frameshift or disrupt a CI domain'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4305C>G"
        self.variant["Pos"] = "43082456"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA1_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GAGGTATGT',
                                                                                       'varWindowPosition': 2,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 7.64,
                                                                                       'altMaxEntScanScore': 9.81,
                                                                                       'refSeq': 'GTGGTATGT',
                                                                                       'varStart': 1,
                                                                                       'altZScore': 0.8037409012613367,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -0.12799118135281953})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326244)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.4044271515695557,
                                                                            'sequence': 'AAGGTAAAT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32326283,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon6',
                                                                            'maxEntScanScore': 8.88})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['478', '516+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32326244', 'c.478', 'g.32326283', 'c.516+1'])
    def test_getPriorProbDeNovoDonorSNSNoFrameshiftOrCIDisruptionBRCA2(self, getVarType, varInExon, varInSpliceRegion,
                                                                       varInIneligibleDeNovoExon, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                       getNewSplicePosition, getClosestSpliceSiteScores,
                                                                       getDeNovoSpliceFrameshiftStatus, getDeNovoFrameshiftAndCIStatus,
                                                                       convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests that prior prob is changed to low prob (0.02) when de novo splicing does not cause a frameshift or disrupt a CI domain'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.476T>A"
        self.variant["Pos"] = "32326242"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=True)
        self.assertEquals(priorProb["priorProb"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInIneligibleDeNovoExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTACCG',
                                                                                       'varWindowPosition': 4,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 1.49,
                                                                                       'altMaxEntScanScore': 9.67,
                                                                                       'refSeq': 'AAGATACCG',
                                                                                       'varStart': 3,
                                                                                       'altZScore': 0.743629153995907,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.7686143647984682})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43097272)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 1.1729987773204027,
                                                                            'sequence': 'CAGGTGAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43097243,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon9',
                                                                            'maxEntScanScore': 10.67})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['566', '593+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43097271', 'c.566', 'g.43097243', 'c.593+1'])
    def test_getPriorProbDeNovoDonorSNSExonCappedProbBRCA1(self, getVarType, varInSpliceRegion, varInExon,
                                                           varInIneligibleDeNovoExon, getMaxMaxEntScanScoreSlidingWindowSNS,
                                                           getNewSplicePosition, getClosestSpliceSiteScores,
                                                           getDeNovoSpliceFrameshiftStatus,
                                                           getDeNovoFrameshiftAndCIStatus, convertGenomicPosToTranscriptPos,
                                                           formatSplicePosition):
        '''Tests that de novo prior prob is assigned correctly for BRCA1 exonic variant in special case of skipped exon'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.566A>G"
        self.variant["Pos"] = "43097271"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAGGTTAAT',
                                                                                       'varWindowPosition': 5,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -2.45,
                                                                                       'altMaxEntScanScore': 5.2,
                                                                                       'refSeq': 'AAGGGTAAT',
                                                                                       'varStart': 4,
                                                                                       'altZScore': -1.175653062264589,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.460330680696982})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43095847)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.8407447560714822,
                                                                            'sequence': 'AGGGTAATG',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43095845,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon10',
                                                                            'maxEntScanScore': 5.98})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 5.98,
                                                                               'altZScore': -4.490386554329697,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 3,
                                                                               'refZScore': -0.8407447560714822,
                                                                               'altMaxEntScanScore': -2.52,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.5,
                                                                               'altSeq': 'AGGTTAATG',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'AGGGTAATG'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.getDeNovoFrameshiftAndCIStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['670', '670+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43095846', 'c.670', 'g.43095845', 'c.670+1'])
    def test_getPriorProbDeNovoDonorSNSSpliceSiteCappedProbBRCA1(self, getVarType, varInSpliceRegion, varInExon,
                                                                 getMaxMaxEntScanScoreSlidingWindowSNS,
                                                                 getNewSplicePosition, getClosestSpliceSiteScores,
                                                                 getPriorProbRefSpliceDonorSNS, getDeNovoSpliceFrameshiftStatus,
                                                                 getDeNovoFrameshiftAndCIStatus, convertGenomicPosToTranscriptPos,
                                                                 formatSplicePosition):
        '''Tests that de novo prior prob is assigned correctly for BRCA1 splice site variant in special case of skipped exon'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.670+1g>T"
        self.variant["Pos"] = "43095845"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoDonorSNS(self.variant, boundaries, STD_EXONIC_PORTION, GENOME,
                                                             BRCA2_RefSeq, deNovoDonorInRefAcc=False)
        self.assertEquals(priorProb["priorProb"], priorProbs["capped"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 1)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
            
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTTTACATCTAAATGTCCAATTT',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -3.96,
                                                                                       'altMaxEntScanScore': -4.11,
                                                                                       'refSeq': 'TTTTACATCTAAATGTCCATTTT',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -4.969838672904024,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -4.908203170286155})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43049200)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.2815061501383356,
                                                                            'sequence': 'CATCTAAATGTCCATTTTAGATC',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 43049195,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon22',
                                                                            'maxEntScanScore': 8.67})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 8.67,
                                                                                  'altZScore': -0.4827740823232286,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 14,
                                                                                  'refZScore': 0.2815061501383356,
                                                                                  'altMaxEntScanScore': 6.81,
                                                                                  'enigmaClass': 'class_3',
                                                                                  'priorProb': 0.34,
                                                                                  'altSeq': 'CATCTAAATGTCCAATTTAGATC',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'CATCTAAATGTCCATTTTAGATC'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['5333-6', '5333-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43049200', 'c.5333-6', 'g.43049195', 'c.5333-1'])
    def test_getPriorProbDeNovoAccSNSFalseAltLessRefBRCA1(self, getVarType, varInSpliceRegion,
                                                          getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                          getClosestSpliceSiteScores, getPriorProbRefSpliceAcceptorSNS,
                                                          getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                          formatSplicePosition):
        '''Tests that function works for variant in splice site altZ < refZ'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5333-6T>A"
        self.variant["Pos"] = "43049200"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA1_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TCTTACAGTCAGAAACGAAGAAG',
                                                                                       'varWindowPosition': 16,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -11.02,
                                                                                       'altMaxEntScanScore': -11.86,
                                                                                       'refSeq': 'TCTTACAGTCAGAAATGAAGAAG',
                                                                                       'varStart': 15,
                                                                                       'altZScore': -8.154339641493873,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -7.8091808268338125})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32329454)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.018528005635431572,
                                                                            'sequence': 'CATAAATTTTTATCTTACAGTCA',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 32329442,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon8',
                                                                            'maxEntScanScore': 8.03})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['643', '632-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32329454', 'c.643', 'g.32329442', 'c.632-1'])
    def test_getPriorProbDeNovoAccSNSFalseAltLessRefBRCA2(self, getVarType, varInSpliceRegion,
                                                          getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                          getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                          convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests that function works for variant in de novo splice region altZ < refZ'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.639T>C"
        self.variant["Pos"] = "32329450"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA2_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GGACTCTGTCTTTTCCCTATAGC',
                                                                                        'varWindowPosition': 23,
                                                                                        'inExonicPortion': True,
                                                                                        'refMaxEntScanScore': -0.03,
                                                                                        'altMaxEntScanScore': 0.26,
                                                                                        'refSeq': 'GGACTCTGTCTTTTCCCTATAGT',
                                                                                        'varStart': 22,
                                                                                        'altZScore': -3.174191029970134,
                                                                                        'varLength': 1,
                                                                                        'refZScore': -3.2933530016980126})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43095925)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.8280076066834324,
                                                                            'sequence': 'ACTCTGTCTTTTCCCTATAGTGT',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 43095923,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon10',
                                                                            'maxEntScanScore': 10.0})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 10.0,
                                                                                  'altZScore': 1.2224748234377885,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 20,
                                                                                  'refZScore': 0.8280076066834324,
                                                                                  'altMaxEntScanScore': 10.96,
                                                                                  'enigmaClass': 'class_2',
                                                                                  'priorProb': 0.04,
                                                                                  'altSeq': 'ACTCTGTCTTTTCCCTATAGCGT',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'ACTCTGTCTTTTCCCTATAGTGT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['594-3', '594-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43095925', 'c.594-3', 'g.43095923', 'c.594-1'])
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterRefBRCA1(self, getVarType, varInSpliceRegion,
                                                            getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                            getClosestSpliceSiteScores, getPriorProbRefSpliceAcceptorSNS,
                                                            getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                            formatSplicePosition):
        '''Tests that function works for variant in ref splice site altZ > refZ, altZ < closestAltZ'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.594T>C"
        self.variant["Pos"] = "43095922"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA1_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, True])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'AAATCAATATATTTATTAAGTTG',
                                                                                       'varWindowPosition': 20,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -7.9,
                                                                                       'altMaxEntScanScore': 0.7,
                                                                                       'refSeq': 'AAATCAATATATTTATTAATTTG',
                                                                                       'varStart': 19,
                                                                                       'altZScore': -2.9933935556243876,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -6.527162372382157})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32370393)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.5305776268269857,
                                                                            'sequence': 'ATATTTATTAATTTGTCCAGATT',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 32370401,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon19',
                                                                            'maxEntScanScore': 4.26})
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 4.26,
                                                                                  'altZScore': -4.337047512693911,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 11,
                                                                                  'refZScore': -1.5305776268269857,
                                                                                  'altMaxEntScanScore': -2.57,
                                                                                  'enigmaClass': 'class_4',
                                                                                  'priorProb': 0.97,
                                                                                  'altSeq': 'ATATTTATTAAGTTGTCCAGATT',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'ATATTTATTAATTTGTCCAGATT'})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['8332-9', '8332-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32370393', 'c.8332-9', 'g.32370401', 'c.8332-1'])
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterRefGreaterClosestAltBRCA2(self, getVarType, varInSpliceRegion,
                                                                             getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                             getClosestSpliceSiteScores, getPriorProbRefSpliceAcceptorSNS,
                                                                             getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                                             formatSplicePosition):
        '''Tests function for variant in ref splice site altZ > refZ and altZ > closestALtZ'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8332-9T>G"
        self.variant["Pos"] = "32370393"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA2_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], 1)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'ATTTATCGTTTTTGAAGCAGATG',
                                                                                       'varWindowPosition': 22,
                                                                                       'inExonicPortion': True,
                                                                                       'refMaxEntScanScore': 3.17,
                                                                                       'altMaxEntScanScore': 4.73,
                                                                                       'refSeq': 'ATTTATCGTTTTTGAAGCAGAGG',
                                                                                       'varStart': 21,
                                                                                       'altZScore': -1.3374530519576655,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -1.9784622791834936})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43082573)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.4031975880833913,
                                                                            'sequence': 'GCCATTTATCGTTTTTGAAGCAG',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 43082576,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon13',
                                                                            'maxEntScanScore': 4.57})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = False)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['4188', '4186-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.43082573', 'c.4188', 'g.43082576', 'c.4186-1'])
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterClosestRefBRCA1(self, getVarType, varInSpliceRegion,
                                                                   getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                   getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                   convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests function for variant in de novo splice region altZ > refZ and altZ > closestRefZ'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4190G>T"
        self.variant["Pos"] = "43082571"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA1_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 0)
        
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInSpliceRegion', side_effect = [True, False])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'GTCCAGATTTCTCCTAACAGTAC',
                                                                                       'varWindowPosition': 13,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': 2.86,
                                                                                       'altMaxEntScanScore': 5.26,
                                                                                       'refSeq': 'GTCCAGATTTCTGCTAACAGTAC',
                                                                                       'varStart': 12,
                                                                                       'altZScore': -1.1196742760411986,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -2.1058423179270873})
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32370415)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -1.5305776268269857,
                                                                            'sequence': 'ATATTTATTAATTTGTCCAGATT',
                                                                            'exonStart': 20,
                                                                            'genomicSplicePos': 32370401,
                                                                            'intronStart': 0,
                                                                            'exonName': 'exon19',
                                                                            'maxEntScanScore': 4.26})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['8345', '8332-1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect = ['g.32370415', 'c.8345', 'g.32370401', 'c.8332-1'])
    def test_getPriorProbDeNovoAccSNSFlagAltGreaterClosestRefBRCA2(self, getVarType, varInSpliceRegion,
                                                                   getMaxMaxEntScanScoreSlidingWindowSNS, getNewSplicePosition,
                                                                   getClosestSpliceSiteScores, getDeNovoSpliceFrameshiftStatus,
                                                                   convertGenomicPosToTranscriptPos, formatSplicePosition):
        '''Tests function for variant in de novo splice region altZ > refZ and altZ > closestRefZ'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8338G>C"
        self.variant["Pos"] = "32370408"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbDeNovoAcceptorSNS(self.variant, STD_EXONIC_PORTION, STD_DE_NOVO_LENGTH,
                                                                GENOME, BRCA2_RefSeq)
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], 1)

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 10.08,
                                                                               'altZScore': 0.159686466274593,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 0.9196706995589503,
                                                                               'altMaxEntScanScore': 8.31,
                                                                               'enigmaClass': 'class_2',
                                                                               'priorProb': 0.04,
                                                                               'altSeq': 'CATGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'CAAGTAAGT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 0.159686466274593,
                                                                            'varStart': 6,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'TTTGCATGT',
                                                                            'altZScore': -5.66256562600557,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'CATGTAAGT',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -0.35,
                                                                            'closestTranscriptSplicePos': 'c.134+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.131',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 8.31,
                                                                            'closestRefZScore': 0.9196706995589503,
                                                                            'closestRefMaxEntScanScore': 10.08,
                                                                            'refZScore': -3.558654471715541,
                                                                            'altGreaterRefFlag': 0,
                                                                            'closestGenomicSplicePos': 'g.43115725',
                                                                            'altMaxEntScanScore': -5.25,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.43115729',
                                                                            'closestRefSeq': 'CAAGTAAGT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 0,
                                                                            'refSeq': 'TTTGCAAGT'})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_3',
                                                                        'priorProb': 0.29})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbSpliceDonorSNSLowDeNovoProbBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                          getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                          getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (no de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = "17"
        self.variant["HGVS_cDNA"] = "c.134A>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43115726"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is NOT flagged as a de novo splice donor or acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["low"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference and de novo donor values and closest donor site
        self.assertNotEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertNotEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor site
        self.assertEquals(priorProb["altRefAccZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefMES"], "N/A")
        self.assertEquals(priorProb["closestAccAltMES"], "N/A")
        # checks that splic positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")
        
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 8.88,
                                                                               'altZScore': -0.9051501995701567,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 1,
                                                                               'refZScore': 0.4044271515695557,
                                                                               'altMaxEntScanScore': 5.83,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'AGGGTAAAT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'AAGGTAAAT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': -0.9051501995701567,
                                                                            'varStart': 7,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'TTTGTGAGG',
                                                                            'altZScore': -2.7385584911657537,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'AGGGTAAAT',
                                                                            'frameshiftFlag': 0,
                                                                            'refMaxEntScanScore': -9.44,
                                                                            'closestTranscriptSplicePos': 'c.516+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.511',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 5.83,
                                                                            'closestRefZScore': 0.4044271515695557,
                                                                            'closestRefMaxEntScanScore': 8.88,
                                                                            'refZScore': -7.461624347735207,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.32326283',
                                                                            'altMaxEntScanScore': 1.56,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32326277',
                                                                            'closestRefSeq': 'AAGGTAAAT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 0,
                                                                            'refSeq': 'TTTGTGAAG'})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    def test_getPriorProbSpliceDonorSNSWithDeNovoBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                       getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                       getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (with de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.515A>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32326281"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        # checks that variant splice site flag and de novo splice flag are assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 0)
        # checks that variant is not flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference donor score and de novo splice donor score and closest donor
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorAltSeq"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that splice positions are present for de novo and closest donor and are NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceDonorSNS', return_value = {'refMaxEntScanScore': 9.66,
                                                                               'altZScore': -0.5358923235110902,
                                                                               'varLength': 1,
                                                                               'exonStart': 0,
                                                                               'intronStart': 3,
                                                                               'varStart': 2,
                                                                               'refZScore': 0.7393354577626622,
                                                                               'altMaxEntScanScore': 6.69,
                                                                               'enigmaClass': 'class_3',
                                                                               'priorProb': 0.34,
                                                                               'altSeq': 'TATGTAAGT',
                                                                               'spliceSite': 1,
                                                                               'refSeq': 'TAGGTAAGT'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': -0.5358923235110902,
                                                                            'varStart': 6,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'GACTTATGT', 
                                                                            'altZScore': -3.6960527511793795,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'TATGTAAGT',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -1.72,
                                                                            'closestTranscriptSplicePos': 'c.316+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.313',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 6.69,
                                                                            'closestRefZScore': 0.7393354577626622,
                                                                            'closestRefMaxEntScanScore': 9.66,
                                                                            'refZScore': -4.1468908556701,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.32319326',
                                                                            'altMaxEntScanScore': -0.67,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32319322',
                                                                            'closestRefSeq': 'TAGGTAAGT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 0,
                                                                            'refSeq': 'GACTTAGGT'})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': '-',
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'lowMESFlag': '-',
                                                                                     'frameshiftFlag': 1,
                                                                                     'isDivisibleFlag': '-',
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    def test_getPriorProbSpliceDonorSNSNonsenseBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                     getPriorProbRefSpliceDonorSNS, getPriorProbDeNovoDonorSNS,
                                                     getPriorProbProteinSNS, getVarConsequences,
                                                     getPriorProbSpliceRescueNonsenseSNS):
        '''Tests function for nonsense variant in reference splice donor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.316G>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32319325"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbSpliceDonorSNS(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        # checks that variant splice site flag and de novo splice flag are assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        # checks that variant is not flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference donor score and de novo splice donor score and closest donor 
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertNotEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that scores and sequences are not present for ref splice acceptor site or de novo splice acceptor sites and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertEquals(priorProb["closestAccAltZ"], "N/A")
        # checks that splice posiitons are present for de novo and closest donor and are NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that splice rescue and splice flag are equal to zero
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that frameshift is equal to 1, because nonsense variant causes frameshift mutation
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        # checks that other nonsense rescue flags are equal to zero or "-" as appropriate
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "-")
        self.assertEquals(priorProb["isDivisibleFlag"], "-")
        self.assertEquals(priorProb["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value =  {'refMaxEntScanScore': 10.37,
                                                                                   'altZScore': 1.4936710349564073,
                                                                                   'varLength': 1,
                                                                                   'exonStart': 20,
                                                                                   'intronStart': 0,
                                                                                   'varStart': 20,
                                                                                   'refZScore': 0.9800418464741734,
                                                                                   'altMaxEntScanScore': 11.62,
                                                                                   'enigmaClass': 'class_2',
                                                                                   'priorProb': 0.04,
                                                                                   'altSeq': 'ATATTTTCTCCCCATTGCAGGAC',
                                                                                   'spliceSite': 1,
                                                                                   'refSeq': 'ATATTTTCTCCCCATTGCAGCAC'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'exonStart': 20,
                                                                               'closestAltZScore': 1.4936710349564073,
                                                                               'varStart': 19,
                                                                               'closestExonStart': 20,
                                                                               'altSeq': 'TATTTTCTCCCCATTGCAGGACA',
                                                                               'altZScore': -5.705355670810582,
                                                                               'altGreaterClosestRefFlag': 0,
                                                                               'closestAltSeq': 'ATATTTTCTCCCCATTGCAGGAC',
                                                                               'frameshiftFlag': 1,
                                                                               'refMaxEntScanScore': -13.96,
                                                                               'closestTranscriptSplicePos': 'c.7008-1',
                                                                               'varLength': 1,
                                                                               'transcriptSplicePos': 'c.7008',
                                                                               'intronStart': 0,
                                                                               'closestAltMaxEntScanScore': 11.62,
                                                                               'closestRefZScore': 0.9800418464741734,
                                                                               'closestRefMaxEntScanScore': 10.37,
                                                                               'refZScore': -9.017236678144027,
                                                                               'altGreaterRefFlag': 1,
                                                                               'closestGenomicSplicePos': 'g.32354860',
                                                                               'altMaxEntScanScore': -5.9,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'genomicSplicePos': 'g.32354861',
                                                                               'closestRefSeq': 'ATATTTTCTCCCCATTGCAGCAC',
                                                                               'closestIntronStart': 0,
                                                                               'altGreaterClosestAltFlag': 0,
                                                                               'refSeq': 'TATTTTCTCCCCATTGCAGCACA'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 3,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'CAGGACAAC',
                                                                            'altZScore': -5.928774792466758,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -14.15,
                                                                            'closestTranscriptSplicePos': 'c.7435+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.7008',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': -0.9867304280018111,
                                                                            'closestRefMaxEntScanScore': 5.64,
                                                                            'refZScore': -9.483955273593583,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.32355289',
                                                                            'altMaxEntScanScore': -5.87,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32354861',
                                                                            'closestRefSeq': 'TAGGTATTG',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'CAGCACAAC'})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "splice_region_variant")
    def test_getPriorProbSpliceAcceptorSNSDeNovoAccBRCA2(self, varInSpliceRegion, getVarType, varInExon,
                                                         getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoAcceptorSNS,
                                                         getPriorProbDeNovoDonorSNS, getPriorProbProteinSNS, getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (no de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["Chr"] = "13"
        self.variant["HGVS_cDNA"] = "c.7008C>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32354861"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is correctly flagged as a potential de novo splice donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], 0)
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], 1)
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["low"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that protein prior prob, ref prior prob, and de novo prior probs are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["low"])
        self.assertEquals(priorProb["deNovoAccPrior"], "N/A")
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        # checks that scores and sequences are present for reference acceptor value and de novo donor/acceptor value and closest splice sites
        self.assertNotEquals(priorProb["refRefAccZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertNotEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertNotEquals(priorProb["closestAccAltZ"], "N/A")
        # checks that splice positions are present for de novo and closest splice donor/acceptor
        self.assertNotEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        # checks that scores and sequences are not present for ref splice donor site or alt splice donor
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")
        
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 4.57,
                                                                                  'altZScore': -2.286639792272834,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 4,
                                                                                  'refZScore': -1.4031975880833913,
                                                                                  'altMaxEntScanScore': 2.42,
                                                                                  'enigmaClass': 'class_4',
                                                                                  'priorProb': 0.97,
                                                                                  'altSeq': 'GCCAGTTATCGTTTTTGAAGCAG',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'GCCATTTATCGTTTTTGAAGCAG'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'exonStart': 20,
                                                                               'closestAltZScore': -2.286639792272834,
                                                                               'varStart': 19,
                                                                               'closestExonStart': 20,
                                                                               'altSeq': 'TTTCATTTTCTTGGTGCCAGTTA',
                                                                               'altZScore': -0.5238644174018071,
                                                                               'altGreaterClosestRefFlag': 1,
                                                                               'closestAltSeq': 'GCCAGTTATCGTTTTTGAAGCAG',
                                                                               'frameshiftFlag': 0,
                                                                               'refMaxEntScanScore': -1.89,
                                                                               'closestTranscriptSplicePos': 'c.4186-1',
                                                                               'varLength': 1,
                                                                               'transcriptSplicePos': 'c.4186-16',
                                                                               'intronStart': 0,
                                                                               'closestAltMaxEntScanScore': 2.42,
                                                                               'closestRefZScore': -1.4031975880833913,
                                                                               'closestRefMaxEntScanScore': 4.57,
                                                                               'refZScore': -4.057633234159576,
                                                                               'altGreaterRefFlag': 1,
                                                                               'closestGenomicSplicePos': 'g.43082576',
                                                                               'altMaxEntScanScore': 6.71,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'genomicSplicePos': 'g.43082591',
                                                                               'closestRefSeq': 'GCCATTTATCGTTTTTGAAGCAG',
                                                                               'closestIntronStart': 0,
                                                                               'altGreaterClosestAltFlag': 1,
                                                                               'refSeq': 'TTTCATTTTCTTGGTGCCATTTA'})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    def test_getPriorProbSpliceAcceptorSNSWithDeNovoBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                          getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoAcceptorSNS,
                                                          getVarConsequences):
        '''Tests that applicable prior for a variant in a reference splice site is assigned correctly (with de novo splicing)'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = 17
        self.variant["HGVS_cDNA"] = "c.4186-16t>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43082591"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is flagged as a de novo splice acceptor
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], 1)
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], 0)
        # checks that variant is not flagged as a de novo donor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["high"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class4"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["high"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for reference acceptor score and de novo splice acceptor score and closest acceptor
        self.assertNotEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertNotEquals(priorProb["refRefAccZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that scores and sequences are not present for ref splice donor site or de novo splice donor sites and closest donor
        self.assertEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorRefSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorAltSeq"], "N/A")
        # checks that splice positions are present for de novo and closest acceptor and are NOT present for de novo and closest donor
        self.assertNotEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        # checks that splice rescue, splice flag, and splice rescue flags are all equal to approriate value (either 0 or N/A)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbRefSpliceAcceptorSNS', return_value = {'refMaxEntScanScore': 3.71,
                                                                                  'altZScore': -2.0400977818013613,
                                                                                  'varLength': 1,
                                                                                  'exonStart': 20,
                                                                                  'intronStart': 0,
                                                                                  'varStart': 20,
                                                                                  'refZScore': -1.7565744697591685,
                                                                                  'altMaxEntScanScore': 3.02,
                                                                                  'enigmaClass': 'class_3',
                                                                                  'priorProb': 0.34,
                                                                                  'altSeq': 'TTCTTTACCATACTGTTTAGTAG',
                                                                                  'spliceSite': 1,
                                                                                  'refSeq': 'TTCTTTACCATACTGTTTAGCAG'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 0,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'TAGGAAACC',
                                                                            'altZScore': -4.061016931005201,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': 0.48,
                                                                            'closestTranscriptSplicePos': 'c.547+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.445',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 0.49030107623445457,
                                                                            'closestRefMaxEntScanScore': 9.08,
                                                                            'refZScore': -3.2022776843562095,
                                                                            'altGreaterRefFlag': 0,
                                                                            'closestGenomicSplicePos': 'g.43099774',
                                                                            'altMaxEntScanScore': -1.52,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.43099877',
                                                                            'closestRefSeq': 'TGGGTAAGG',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'CAGGAAACC'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'exonStart': 20,
                                                                               'closestAltZScore': -2.0400977818013613,
                                                                               'varStart': 17,
                                                                               'closestExonStart': 20,
                                                                               'altSeq': 'TTTACCATACTGTTTAGTAGGAA',
                                                                               'altZScore': -1.8716274079791886,
                                                                               'altGreaterClosestRefFlag': 0,
                                                                               'closestAltSeq': 'TTCTTTACCATACTGTTTAGTAG',
                                                                               'frameshiftFlag': 0,
                                                                               'refMaxEntScanScore': 4.78,
                                                                               'closestTranscriptSplicePos': 'c.442-1',
                                                                               'varLength': 1,
                                                                               'transcriptSplicePos': 'c.444',
                                                                               'intronStart': 0,
                                                                               'closestAltMaxEntScanScore': 3.02,
                                                                               'closestRefZScore': -1.7565744697591685,
                                                                               'closestRefMaxEntScanScore': 3.71,
                                                                               'refZScore': -1.3169078844183761,
                                                                               'altGreaterRefFlag': 0,
                                                                               'closestGenomicSplicePos': 'g.43099881',
                                                                               'altMaxEntScanScore': 3.43,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'genomicSplicePos': 'g.43099878',
                                                                               'closestRefSeq': 'TTCTTTACCATACTGTTTAGCAG',
                                                                               'closestIntronStart': 0,
                                                                               'altGreaterClosestAltFlag': 1,
                                                                               'refSeq': 'TTTACCATACTGTTTAGCAGGAA'})
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': '-',
                                                                                     'inExonicPortionFlag': 1,
                                                                                     'lowMESFlag': '-',
                                                                                     'frameshiftFlag': '-',
                                                                                     'isDivisibleFlag': '-',
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    def test_getPriorProbSpliceAcceptorSNSNonsenseBRCA1(self, varInSpliceRegion, getVarType, varInExon,
                                                        getPriorProbRefSpliceAcceptorSNS, getPriorProbDeNovoDonorSNS,
                                                        getPriorProbDeNovoAcceptorSNS, getPriorProbProteinSNS,
                                                        getVarConsequences, getPriorProbSpliceRescueNonsenseSNS):
        '''Tests function with nonsense variant in reference acceptor site'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["Chr"] = "17"
        self.variant["HGVS_cDNA"] = "c.442C>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43099880"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbSpliceAcceptorSNS(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        # checks that variant splice site flag is assigned correctly
        self.assertEquals(priorProb["spliceSite"], 1)
        # checks that variant is flagged correctly as a de novo splice donor or acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], 1)
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], 0)
        # checks that prior prob and enigma class are appropriate based on applicable prior
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior prob, ref prior prob, and de novo prior prob are set appropriately
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["moderate"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that a score and sequence are NOT present for reference donor score and are present for de novo splice donor score
        self.assertNotEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        # checks that scores and sequences are present for ref splice acceptor site or de novo splice acceptor sites
        self.assertNotEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["refRefAccMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertNotEquals(priorProb["closestAccAltZ"], "N/A")
        # checks that splic positions are present for de novo and closest donor and acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that inExonicPortion flag is equal to 1
        self.assertEquals(priorProb["inExonicPortionFlag"], 1)
        # checks that splice rescue, splice flag, and splice rescue flags are equal to zero or "-" as approriate
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "-")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "-")
        self.assertEquals(priorProb["isDivisibleFlag"], "-")
        self.assertEquals(priorProb["lowMESFlag"], "-")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getPriorProbProteinSNS(self, getVarType):
        '''Tests that function parses data from variantData correctly and returns correct prior prob/class'''
        # checks for BRCA1 variant
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["HGVS_cDNA"] = "c.592A>T"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbProteinSNS(self.variant, variantData)
        self.assertEquals(priorProb["priorProb"], priorProbs["proteinMod"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])

        # checks for BRCA2 variant that has pyhgvs_cDNA instead of HGVS_cDNA
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["HGVS_cDNA"] = "-"
        self.variant["pyhgvs_cDNA"] = "NM_000059.3:c.620C>T"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbProteinSNS(self.variant, variantData)
        self.assertEquals(priorProb["priorProb"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["class3"])

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inGreyZone"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {"priorProb": 0.02,
                                                                        "enigmaClass": "class_2"})
    def test_getPriorProbInGreyZoneSNSLowProb(self, getVarType, getVarLocationSNS, getPriorProbProteinSNS):
        '''Tests that prior prob is correct for variant in the grey zone with a low protein prior'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9930A>G"
        self.variant["Pos"] = "32398443"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbInGreyZoneSNS(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inGreyZone"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {"priorProb": 0.99,
                                                                        "enigmaClass": "class_5"})
    def test_getPriorProbInGreyZoneSNSHighProb(self, getVarType, getVarLocationSNS, getPriorProbProteinSNS):
        '''Tests that prior prob is correct for variant in the grey zone with a high protein prior'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.9943A>T"
        self.variant["Pos"] = "32398456"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInGreyZoneSNS(self.variant, boundaries, variantData)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["capped"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        self.assertEquals(priorProb["proteinPrior"], priorProbs["capped"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_2',
                                                                        'priorProb': 0.02})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 2,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'AGGGTCAGC',
                                                                            'altZScore': -1.8454696746508026,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -4.51,
                                                                            'closestTranscriptSplicePos': 'c.4986+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.4758',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': -0.870800629704197,
                                                                            'closestRefMaxEntScanScore': 5.91,
                                                                            'refZScore': -5.344832104745444,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.43070927',
                                                                            'altMaxEntScanScore': 3.64,
                                                                            'enigmaClass': 'class_3',
                                                                            'priorProb': 0.3,
                                                                            'genomicSplicePos': 'g.43071156',
                                                                            'closestRefSeq': 'TTTGTGAGT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'AGAGTCAGC'})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSDeNovoDonorBRCA1(self, getVarLocationSNS, getVarType, getPriorProbProteinSNS,
                                                   getVarConsequences, getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that function works correctly for missense variant in exon with de novo donor score, no de novo acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4757A>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43071157"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoMod"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccZ"], "N/A")
        self.assertEquals(priorProb["altRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertEquals(priorProb["closestAccAltZ"], "N/A")
        # checks that splice positions are present for de novo and closest donor and are NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, splice rescue flags) are all equal to correct values
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_3',
                                                                        'priorProb': 0.81})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "missense_variant")
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 3,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'ATGCTACGG',
                                                                            'altZScore': -3.4384309771846815,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': 0.02,
                                                                            'closestTranscriptSplicePos': 'c.8331+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.7982',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 0.4044271515695557,
                                                                            'closestRefMaxEntScanScore': 8.88,
                                                                            'refZScore': -3.3997877110854775,
                                                                            'altGreaterRefFlag': 0,
                                                                            'closestGenomicSplicePos': 'g.32363534',
                                                                            'altMaxEntScanScore': -0.07,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32363184',
                                                                            'closestRefSeq': 'AAGGTAAAT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'ATGATACGG'})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'exonStart': 20,
                                                                               'closestAltZScore': 'N/A',
                                                                               'varStart': 4,
                                                                               'closestExonStart': 20,
                                                                               'altSeq': 'TATGCTACGGAAATTGATAGAAG',
                                                                               'altZScore': -4.501408853008226,
                                                                               'altGreaterClosestRefFlag': 0,
                                                                               'closestAltSeq': 'N/A',
                                                                               'frameshiftFlag': 0,
                                                                               'refMaxEntScanScore': -3.14,
                                                                               'closestTranscriptSplicePos': 'c.7977-1',
                                                                               'varLength': 1,
                                                                               'transcriptSplicePos': 'c.7997',
                                                                               'intronStart': 0,
                                                                               'closestAltMaxEntScanScore': 'N/A',
                                                                               'closestRefZScore': 1.444362632862113,
                                                                               'closestRefMaxEntScanScore': 11.5,
                                                                               'refZScore': -4.57126242264181,
                                                                               'altGreaterRefFlag': 1,
                                                                               'closestGenomicSplicePos': 'g.32363178',
                                                                               'altMaxEntScanScore': -2.97,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'genomicSplicePos': 'g.32363199',
                                                                               'closestRefSeq': 'ATTTTTGTTTTCACTTTTAGATA',
                                                                               'closestIntronStart': 0,
                                                                               'altGreaterClosestAltFlag': 'N/A',
                                                                               'refSeq': 'TATGATACGGAAATTGATAGAAG'})
    def test_getPriorProbInExonSNSEnigmaCIDeNovoAcceptorBRCA2(self, getVarLocationSNS, getVarType, getPriorProbProteinSNS,
                                                              getVarConsequences, getPriorProbDeNovoDonorSNS,
                                                              varInSpliceRegion, getPriorProbDeNovoAcceptorSNS):
        '''Tests that function works correctly for missense variant in ENIGMA CI domain  with de novo acceptor score, no de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.7982A>C"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32363184"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class3"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["proteinHigh"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo acceptor and de novo donor and closest donor/acceptor
        self.assertNotEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], 0)
        # checks that splice positions are present for de novo and closest donor and acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor and ref splice donor
        self.assertEquals(priorProb["altRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, splice rescue flags) are all equal to correct values
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")
        
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inCI"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': '-',
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'lowMESFlag': '-',
                                                                                     'frameshiftFlag': 1,
                                                                                     'isDivisibleFlag': '-',
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 8,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'ATGCTATGT',
                                                                            'altZScore': -3.3740255336860074,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -1.14,
                                                                            'closestTranscriptSplicePos': 'c.80+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.50',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 1.164411384853913,
                                                                            'closestRefMaxEntScanScore': 10.65,
                                                                            'refZScore': -3.897856474141892,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.43124016',
                                                                            'altMaxEntScanScore': 0.08,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.43124047',
                                                                            'closestRefSeq': 'CTGGTAAGT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'ATGCTATGC'})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSPriorsCIWithoutSpliceRescueBRCA1(self, getVarLocationSNS, getVarType, getPriorProbProteinSNS,
                                                                   getVarConsequences, getPriorProbSpliceRescueNonsenseSNS,
                                                                   getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that funciton works correctly for nonsense variant in PRIORS CI domain that does not have splice rescue'''
        boundaries = "priors"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.55C>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124042"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefZ"], "N/A")
        self.assertEquals(priorProb["closestDonorAltZ"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefMES"], "N/A")
        self.assertEquals(priorProb["closestAccAltMES"], "N/A")
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that flags (splice site, splice rescue, splice rescue flags) are all equal to zero or "-" as appropriate
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "-")
        self.assertEquals(priorProb["isDivisibleFlag"], "-")
        self.assertEquals(priorProb["lowMESFlag"], "-")
        # checks that frameshift flag is correct
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        
    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbProteinSNS', return_value = {'enigmaClass': 'class_5',
                                                                        'priorProb': 0.99})
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "stop_gained")
    @mock.patch('calcVarPriors.getPriorProbSpliceRescueNonsenseSNS', return_value = {'CIDomainInRegionFlag': 0,
                                                                                     'inExonicPortionFlag': 0,
                                                                                     'lowMESFlag': 1,
                                                                                     'frameshiftFlag': 0,
                                                                                     'isDivisibleFlag': 0,
                                                                                     'spliceFlag': 0,
                                                                                     'enigmaClass': 'class_5',
                                                                                     'priorProb': 0.99,
                                                                                     'spliceRescue': 0})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 6,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'TACCTGAGT',
                                                                            'altZScore': -3.6230599152142147,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 0,
                                                                            'refMaxEntScanScore': -6.87,
                                                                            'closestTranscriptSplicePos': 'c.7007+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.6993',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 1.1128870300549731,
                                                                            'closestRefMaxEntScanScore': 10.53,
                                                                            'refZScore': -6.358144415791253,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.32346897',
                                                                            'altMaxEntScanScore': -0.5,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32346882',
                                                                            'closestRefSeq': 'TCGGTAAGA',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'TACCTGTGT'})
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    def test_getPriorProbInExonSNSWithoutSpliceRescueBRCA2(self, getVarLocationSNS, getVarType, getPriorProbProteinSNS,
                                                           getVarConsequences, getPriorProbSpliceRescueNonsenseSNS,
                                                           getPriorProbDeNovoDonorSNS, varInSpliceRegion):
        '''Tests that function works correctly for nonsense variant in exon without possibility of splice rescue'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.6996T>A"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32346885"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInExonSNS(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        # checks that applicable prior and enigma class are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class5"])
        # checks that protein prior, ref donor prior, and ref acceptor prior are correct
        self.assertEquals(priorProb["proteinPrior"], priorProbs["pathogenic"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor prior and de novo acceptor prior are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that scores and sequences are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefZ"], "N/A")
        self.assertEquals(priorProb["closestDonorAltZ"], "N/A")
        # checks that flags are correct for de novo donor and acceptor
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that scores and sequences are NOT present for ref splice acceptor, ref splice donor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["altRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that flags (splice site, splice rescue, splice flag, and splice rescue flags) are all correct
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], 0)
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 0)
        self.assertEquals(priorProb["inExonicPortionFlag"], 0)
        self.assertEquals(priorProb["CIDomainInRegionFlag"], 0)
        self.assertEquals(priorProb["isDivisibleFlag"], 0)
        self.assertEquals(priorProb["lowMESFlag"], 1)

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["outBounds"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getPriorProbOutsideTranscriptBoundsSNS(self, getVarLocationSNS, getVarType):
        ''' Tests that function works correctly for both minus and plus strand variants outside transcript boundaries'''
        boundaries = "enigma"
        # checks for minus strand (BRCA1) variant
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-1074C>G"
        self.variant["Pos"] = "43126325"
        self.variant["Ref"] = "G"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbOutsideTranscriptBoundsSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

        # checks for plus strand (BRCA2) variant
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-764A>G"
        self.variant["Pos"] = "32314943"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbOutsideTranscriptBoundsSNS(self.variant, boundaries)
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'CATATGTGT',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -13.63,
                                                                                       'altMaxEntScanScore': -5.58,
                                                                                       'refSeq': 'CATATGTAT',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -5.804257601702654,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -9.260683069464845})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "-")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 43070913)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': -0.870800629704197,
                                                                            'sequence': 'TTTGTGAGT',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 43070927,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon16',
                                                                            'maxEntScanScore': 5.91})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['4986+15', '4986+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect= ['g.43070913', 'c.4986+15', 'g.43070927', 'c.4986+1'])
    def test_getPriorProbIntronicDeNovoDonorSNSWithSpliceFlag(self, varInExon, varInSpliceRegion, getVarType,
                                                              getMaxMaxEntScanScoreSlidingWindowSNS, getVarStrand,
                                                              getNewSplicePosition, getClosestSpliceSiteScores,
                                                              getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                              formatSplicePosition):
        '''Tests that funciton works for variant with predicted splice flag = 1 (altMES > refMES)'''
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4986+19a>G"
        self.variant["Pos"] = "43070909"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbIntronicDeNovoDonorSNS(self.variant, GENOME, BRCA1_RefSeq)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag have the correct values
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 1)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 1)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        # checks that a de novo donor score, sequence, and closest donor sequence are present
        self.assertNotEquals(priorProb["altMaxEntScanScore"], "N/A")
        self.assertNotEquals(priorProb["refSeq"], "N/A")
        self.assertNotEquals(priorProb["closestRefMaxEntScanScore"], "N/A")
        # checks that de novo donor and closest donor splice positions are present
        self.assertNotEquals(priorProb["genomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestTranscriptSplicePos"], "N/A")

    @mock.patch('calcVarPriors.varInExon', return_value = False)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getMaxMaxEntScanScoreSlidingWindowSNS', return_value = {'altSeq': 'TTAACAACT',
                                                                                       'varWindowPosition': 8,
                                                                                       'inExonicPortion': False,
                                                                                       'refMaxEntScanScore': -16.81,
                                                                                       'altMaxEntScanScore': -17.75,
                                                                                       'refSeq': 'TTAACAATT',
                                                                                       'varStart': 7,
                                                                                       'altZScore': -11.029685917561768,
                                                                                       'varLength': 1,
                                                                                       'refZScore': -10.62607847163674})
    @mock.patch('calcVarPriors.getVarStrand', return_value = "+")
    @mock.patch('calcVarPriors.getNewSplicePosition', return_value = 32326215)
    @mock.patch('calcVarPriors.getClosestSpliceSiteScores', return_value = {'zScore': 0.6534615330977633,
                                                                            'sequence': 'CAGGTATGA',
                                                                            'exonStart': 0,
                                                                            'genomicSplicePos': 32326151,
                                                                            'intronStart': 3,
                                                                            'exonName': 'exon5',
                                                                            'maxEntScanScore': 9.46})
    @mock.patch('calcVarPriors.getDeNovoSpliceFrameshiftStatus', return_value = True)
    @mock.patch('calcVarPriors.convertGenomicPosToTranscriptPos', side_effect = ['476-27', '475+1'])
    @mock.patch('calcVarPriors.formatSplicePosition', side_effect= ['g.32326215', 'c.476-27', 'g.32326151', 'c.475+1'])
    def test_getPriorProbIntronicDeNovoDonorSNSNoSpliceFlag(self, varInExon, varInSpliceRegion, getVarType,
                                                            getMaxMaxEntScanScoreSlidingWindowSNS, getVarStrand,
                                                            getNewSplicePosition, getClosestSpliceSiteScores,
                                                            getDeNovoSpliceFrameshiftStatus, convertGenomicPosToTranscriptPos,
                                                            formatSplicePosition):
        '''Tests that function works for variant with predicted splice flag of 0 (refMES > altMES)'''
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.476-23t>C"
        self.variant["Pos"] = "32326219"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbIntronicDeNovoDonorSNS(self.variant, GENOME, BRCA2_RefSeq)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag have the correct values
        self.assertEquals(priorProb["priorProb"], priorProbs["NA"])
        self.assertEquals(priorProb["enigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["altGreaterRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["altGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["spliceFlag"], 0)
        self.assertEquals(priorProb["frameshiftFlag"], 1)
        # checks that a de novo donor score, sequence, and closest donor sequence are present
        self.assertNotEquals(priorProb["refMaxEntScanScore"], "N/A")
        self.assertNotEquals(priorProb["altSeq"], "N/A")
        self.assertNotEquals(priorProb["closestRefSeq"], "N/A")
        # checks that de novo donor and closest donor splice positions are present
        self.assertNotEquals(priorProb["transcriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestGenomicSplicePos"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'spliceFlag': 0,
                                                                                    'exonStart': 0,
                                                                                    'closestAltZScore': 'N/A',
                                                                                    'varStart': 1,
                                                                                    'closestExonStart': 0,
                                                                                    'altSeq': 'CTAATATCT',
                                                                                    'altZScore': -8.698208862909755,
                                                                                    'altGreaterClosestRefFlag': 0,
                                                                                    'closestAltSeq': 'N/A',
                                                                                    'frameshiftFlag': 1,
                                                                                    'refMaxEntScanScore': -10.54,
                                                                                    'closestTranscriptSplicePos': 'c.8754+1',
                                                                                    'varLength': 1,
                                                                                    'transcriptSplicePos': 'c.8755-19',
                                                                                    'intronStart': 3,
                                                                                    'closestAltMaxEntScanScore': 'N/A',
                                                                                    'closestRefZScore': -0.11940378888632941,
                                                                                    'closestRefMaxEntScanScore': 7.66,
                                                                                    'refZScore': -7.933930933392152,
                                                                                    'altGreaterRefFlag': 0,
                                                                                    'closestGenomicSplicePos': 'g.32376792',
                                                                                    'altMaxEntScanScore': -12.32,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'priorProb': 'N/A',
                                                                                    'genomicSplicePos': 'g.32379298',
                                                                                    'closestRefSeq': 'GAGGTGAGA',
                                                                                    'closestIntronStart': 3,
                                                                                    'altGreaterClosestAltFlag': 'N/A',
                                                                                    'refSeq': 'CCAATATCT'})
    def test_getPriorProbInIntronSNSNoDeNovoBRCA2(self, getVarLocationSNS, getVarType, getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for plus strand (BRCA2) variant in intron with ref MES score GREATER than alt MES score'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.8755-21c>T"
        self.variant["Pos"] = "32379296"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInIntronSNS(self.variant, boundaries, GENOME, BRCA2_RefSeq)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag are all set correctly
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that values are present for de novo donor scores, sequences, and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["altDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefZ"], "N/A")
        self.assertEquals(priorProb["closestDonorAltZ"], "N/A")
        # checks that values are NOT present for ref donor/acceptor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["refRefDonorMES"], "N/A")
        self.assertEquals(priorProb["altRefAccZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefMES"], "N/A")
        self.assertEquals(priorProb["closestAccAltMES"], "N/A")
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inIntron"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'spliceFlag': 1,
                                                                                    'exonStart': 0,
                                                                                    'closestAltZScore': 'N/A',
                                                                                    'varStart': 7,
                                                                                    'closestExonStart': 0,
                                                                                    'altSeq': 'TTGGCCAGA',
                                                                                    'altZScore': -5.877250437667818,
                                                                                    'altGreaterClosestRefFlag': 0,
                                                                                    'closestAltSeq': 'N/A',
                                                                                    'frameshiftFlag': 1,
                                                                                    'refMaxEntScanScore': -14.16,
                                                                                    'closestTranscriptSplicePos': 'c.4357+1',
                                                                                    'varLength': 1,
                                                                                    'transcriptSplicePos': 'c.4357+14',
                                                                                    'intronStart': 3,
                                                                                    'closestAltMaxEntScanScore': 'N/A',
                                                                                    'closestRefZScore': -0.5573608046773153,
                                                                                    'closestRefMaxEntScanScore': 6.64,
                                                                                    'refZScore': -9.488248969826827,
                                                                                    'altGreaterRefFlag': 1,
                                                                                    'closestGenomicSplicePos': 'g.43082403',
                                                                                    'altMaxEntScanScore': -5.75,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'priorProb': 'N/A',
                                                                                    'genomicSplicePos': 'g.43082390',
                                                                                    'closestRefSeq': 'AAGGTGTGT',
                                                                                    'closestIntronStart': 3,
                                                                                    'altGreaterClosestAltFlag': 'N/A',
                                                                                    'refSeq': 'TTGGCCAAA'})
    def test_getPriorProbInIntronSNSWithFlagBRCA1(self, getVarLocationSNS, getVarType, getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for minus strand (BRCA1) variant in intron with ref MES score LESS than alt MES score'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.4357+18a>G"
        self.variant["Pos"] = "43082386"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInIntronSNS(self.variant, boundaries, GENOME, BRCA1_RefSeq)
        # checks that prior prob, enigma class, de novo donor flag, and splice flag are all set correctly
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["spliceFlag"], 1)
        # checks that values are present for de novo donor scores, sequences, and closest donor
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoDonorSeq"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that values are NOT present for ref donor/acceptor, de novo acceptor, and closest acceptor
        self.assertEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refRefAccMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that all other priors are set to N/A
        self.assertEquals(priorProb["proteinPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that all flags are equal to zero or N/A
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["spliceSite"], 0)
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "3_prime_UTR_variant")
    def test_getPriorProbInUTRSNS3PrimeBRCA1(self, getVarLocationSNS, getVarType, getVarConsequences):
        '''Tests function for minus strand (BRCA1) variant in 3' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.5592+10g>A"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43045668"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA1_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that there are NOT values present for de novo donor and acceptor, ref donor and acceptor, and closest donor/acceptor
        self.assertEquals(priorProb["refDeNovoDonorMES"], "N/A")
        self.assertEquals(priorProb["altDeNovoAccZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccMES"], "N/A")
        self.assertEquals(priorProb["closestDonorRefZ"], "N/A")
        self.assertEquals(priorProb["closestDonorAltZ"], "N/A")
        self.assertEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that splice positions are NOT present for de novo and closest donor or acceptor
        self.assertEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "3_prime_UTR_variant")
    def test_getPriorProbInUTRSNS3PrimeBRCA2(self, getVarLocationSNS, getVarType, getVarConsequences):
        '''Tests function for plus strand (BRCA2) variant in 3' UTR'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.10257+25t>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32398795"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "G"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA2_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and reference donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that there are NOT values present for de novo donor and acceptor, ref donor and acceptor, and closest donor/acceptor
        self.assertEquals(priorProb["altDeNovoDonorZ"], "N/A")
        self.assertEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["altRefDonorZ"], "N/A")
        self.assertEquals(priorProb["refRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorRefSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorAltSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefMES"], "N/A")
        self.assertEquals(priorProb["closestAccAltMES"], "N/A")
        # checks that splice positions are NOT present for de novo and closest donor or acceptor
        self.assertEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "5_prime_UTR_variant")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = False)
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 4,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'AAGCTTTGG',
                                                                            'altZScore': -4.69219027729221,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 1,
                                                                            'refMaxEntScanScore': -11.17,
                                                                            'closestTranscriptSplicePos': 'c.67+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.-25',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 0.17686125120757246,
                                                                            'closestRefMaxEntScanScore': 8.35,
                                                                            'refZScore': -8.204433796086585,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.32316528',
                                                                            'altMaxEntScanScore': -2.99,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.32316436',
                                                                            'closestRefSeq': 'CAGGTATTG',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'AAGCATTGG'})
    def test_getPriorProbInUTRSNS5PrimeExonDeNovoDonor(self, getVarLocationSNS, getVarType, getVarConsequences, varInExon,
                                                       varInSpliceRegion, getPriorProbDeNovoDonorSNS):
        '''Test function for plus strand (BRCA2) variant in exonic portion of 5' UTR that has de novo donor, no de novo acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-24A>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316437"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA2_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefSeq"], "N/A")
        self.assertEquals(priorProb["closestDonorAltSeq"], "N/A")
        # checks that values are NOT present for de novo acceptor, ref donor/acceptor, and closest acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["refRefDonorZ"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        self.assertEquals(priorProb["closestAccRefMES"], "N/A")
        self.assertEquals(priorProb["closestAccAltMES"], "N/A")
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "5_prime_UTR_variant")
    @mock.patch('calcVarPriors.varInExon', return_value = True)
    @mock.patch('calcVarPriors.varInSpliceRegion', return_value = True)
    @mock.patch('calcVarPriors.getPriorProbDeNovoAcceptorSNS', return_value = {'exonStart': 20,
                                                                               'closestAltZScore': 'N/A',
                                                                               'varStart': 19,
                                                                               'closestExonStart': 20,
                                                                               'altSeq': 'TCTAATGTGTTAAAGTTCAGTGG',
                                                                               'altZScore': -3.3549885043158807,
                                                                               'altGreaterClosestRefFlag': 0,
                                                                               'closestAltSeq': 'N/A',
                                                                               'frameshiftFlag': 1,
                                                                               'refMaxEntScanScore': -8.78,
                                                                               'closestTranscriptSplicePos': 'c.-19-1',
                                                                               'varLength': 1,
                                                                               'transcriptSplicePos': 'c.-15',
                                                                               'intronStart': 0,
                                                                               'closestAltMaxEntScanScore': 'N/A',
                                                                               'closestRefZScore': -1.2675994823240817,
                                                                               'closestRefMaxEntScanScore': 4.9,
                                                                               'refZScore': -6.888757321073649,
                                                                               'altGreaterRefFlag': 1,
                                                                               'closestGenomicSplicePos': 'g.43124116',
                                                                               'altMaxEntScanScore': -0.18,
                                                                               'enigmaClass': 'N/A',
                                                                               'priorProb': 'N/A',
                                                                               'genomicSplicePos': 'g.43124111',
                                                                               'closestRefSeq': 'GTTTTTCTAATGTGTTAAAGTTC',
                                                                               'closestIntronStart': 0,
                                                                               'altGreaterClosestAltFlag': 'N/A',
                                                                               'refSeq': 'TCTAATGTGTTAAAGTTCATTGG'})
    @mock.patch('calcVarPriors.getPriorProbDeNovoDonorSNS', return_value = {'exonStart': 0,
                                                                            'closestAltZScore': 'N/A',
                                                                            'varStart': 7,
                                                                            'closestExonStart': 0,
                                                                            'altSeq': 'AAGTTCAGT',
                                                                            'altZScore': -3.335382267586803,
                                                                            'altGreaterClosestRefFlag': 0,
                                                                            'closestAltSeq': 'N/A',
                                                                            'frameshiftFlag': 0,
                                                                            'refMaxEntScanScore': -4.19,
                                                                            'closestTranscriptSplicePos': 'c.80+1',
                                                                            'varLength': 1,
                                                                            'transcriptSplicePos': 'c.-19',
                                                                            'intronStart': 3,
                                                                            'closestAltMaxEntScanScore': 'N/A',
                                                                            'closestRefZScore': 1.164411384853913,
                                                                            'closestRefMaxEntScanScore': 10.65,
                                                                            'refZScore': -5.207433825281605,
                                                                            'altGreaterRefFlag': 1,
                                                                            'closestGenomicSplicePos': 'g.43124016',
                                                                            'altMaxEntScanScore': 0.17,
                                                                            'enigmaClass': 'class_2',
                                                                            'priorProb': 0.02,
                                                                            'genomicSplicePos': 'g.43124115',
                                                                            'closestRefSeq': 'CTGGTAAGT',
                                                                            'closestIntronStart': 3,
                                                                            'altGreaterClosestAltFlag': 'N/A',
                                                                            'refSeq': 'AAGTTCATT'})
    def test_getPriorProbInUTRSNS5PrimeExonDeNovoAccAndDonor(self, getVarLocationSNS, getVarType, getVarConsequences,
                                                             varInExon, varInSpliceRegion, getPriorProbDeNovoAcceptorSNS,
                                                             getPriorProbDeNovoDonorSNS):
        '''Tests function for minus strand (BRCA1) variant in exonic portion of 5' UTR that has de novo donor and acceptor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-15T>G"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124111"
        self.variant["Ref"] = "A"
        self.variant["Alt"] = "C"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA1_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], 1)
        # checks that values are present for de novo donor and de novo acceptor and closest donor/acceptor
        self.assertNotEquals(priorProb["altDeNovoDonorMES"], "N/A")
        self.assertNotEquals(priorProb["refDeNovoAccMES"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefZ"], "N/A")
        self.assertEquals(priorProb["closestDonorAltZ"], "N/A")
        self.assertNotEquals(priorProb["closestAccRefSeq"], "N/A")
        self.assertEquals(priorProb["closestAccAltSeq"], "N/A")
        # checks that splice positions are present for both de novo and closest donor/acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that values are NOT present for ref donor and acceptor
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'spliceFlag': 1,
                                                                                    'exonStart': 0,
                                                                                    'closestAltZScore': 'N/A',
                                                                                    'varStart': 4,
                                                                                    'closestExonStart': 0,
                                                                                    'altSeq': 'AGTGTATTT',
                                                                                    'altZScore': -5.112972508150215,
                                                                                    'altGreaterClosestRefFlag': 0,
                                                                                    'closestAltSeq': 'N/A',
                                                                                    'frameshiftFlag': 1,
                                                                                    'refMaxEntScanScore': -11.72,
                                                                                    'closestTranscriptSplicePos': 'c.-40+1',
                                                                                    'varLength': 1,
                                                                                    'transcriptSplicePos': 'c.-39-24',
                                                                                    'intronStart': 3,
                                                                                    'closestAltMaxEntScanScore': 'N/A',
                                                                                    'closestRefZScore': -1.287289164328958,
                                                                                    'closestRefMaxEntScanScore': 4.94,
                                                                                    'refZScore': -8.44058708891506,
                                                                                    'altGreaterRefFlag': 1,
                                                                                    'closestGenomicSplicePos': 'g.32315668',
                                                                                    'altMaxEntScanScore': -3.97,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'priorProb': 'N/A',
                                                                                    'genomicSplicePos': 'g.32316398',
                                                                                    'closestRefSeq': 'CGGGTTAGT',
                                                                                    'closestIntronStart': 3,
                                                                                    'altGreaterClosestAltFlag': 'N/A',
                                                                                    'refSeq': 'AGTGCATTT'})
    def test_getPriorProbInUTRSNS5PrimeIntronWithSpliceFlag(self, getVarLocationSNS, getVarType, getVarConsequences,
                                                            getPriorProbIntronicDeNovoDonorSNS):
        '''Tests function for variant in intronic portion of 5' UTR for plus strand (BRCA2) gene that has de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.-39-23c>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32316399"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "T"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA2_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["NA"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["NA"])
        self.assertEquals(priorProb["spliceFlag"], 1)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 1)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 1)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorTranscriptSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccGenomicSplicePos"], "N/A")
        # checks that values are NOT present for de novo acceptor, closest acceptor, and ref donor and acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertEquals(priorProb["closestAccAltZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inUTR"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    @mock.patch('calcVarPriors.getVarConsequences', return_value = "intron_variant")
    @mock.patch('calcVarPriors.getPriorProbIntronicDeNovoDonorSNS', return_value = {'spliceFlag': 0,
                                                                                    'exonStart': 0,
                                                                                    'closestAltZScore': 'N/A',
                                                                                    'varStart': 3,
                                                                                    'closestExonStart': 0,
                                                                                    'altSeq': 'TATTTATGT',
                                                                                    'altZScore': -5.666859322238815,
                                                                                    'altGreaterClosestRefFlag': 0,
                                                                                    'closestAltSeq': 'N/A',
                                                                                    'frameshiftFlag': 0,
                                                                                    'refMaxEntScanScore': -4.93,
                                                                                    'closestTranscriptSplicePos': 'c.-20+1',
                                                                                    'varLength': 1,
                                                                                    'transcriptSplicePos': 'c.-19-24',
                                                                                    'intronStart': 3,
                                                                                    'closestAltMaxEntScanScore': 'N/A',
                                                                                    'closestRefZScore': -0.965261946835586,
                                                                                    'closestRefMaxEntScanScore': 5.69,
                                                                                    'refZScore': -5.525167346541731,
                                                                                    'altGreaterRefFlag': 0,
                                                                                    'closestGenomicSplicePos': 'g.43125270',
                                                                                    'altMaxEntScanScore': -5.26,
                                                                                    'enigmaClass': 'N/A',
                                                                                    'priorProb': 'N/A',
                                                                                    'genomicSplicePos': 'g.43124139',
                                                                                    'closestRefSeq': 'AAGGTAGTA',
                                                                                    'closestIntronStart': 3,
                                                                                    'altGreaterClosestAltFlag': 'N/A',
                                                                                    'refSeq': 'TATATATGT'})
    def test_getPriorProbInUTRSNS5PrimeIntronNoSpliceFlag(self, getVarLocationSNS, getVarType, getVarConsequences,
                                                          getPriorProbIntronicDeNovoDonorSNS):
        '''Tests variant in intronic portion of 5' UTR for minus strand (BRCA1) gene that does not have de novo donor'''
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA1"
        self.variant["Reference_Sequence"] = "NM_007294.3"
        self.variant["HGVS_cDNA"] = "c.-19-24a>T"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "43124139"
        self.variant["Ref"] = "T"
        self.variant["Alt"] = "A"
        priorProb = calcVarPriors.getPriorProbInUTRSNS(self.variant, boundaries, GENOME, BRCA1_RefSeq)
        # checks that applicable prior, applicable class, and splice flag are correct
        self.assertEquals(priorProb["applicablePrior"], priorProbs["deNovoLow"])
        self.assertEquals(priorProb["applicableEnigmaClass"], enigmaClasses["class2"])
        self.assertEquals(priorProb["spliceFlag"], 0)
        # checks that de novo and ref donor and acceptor priors are correct
        self.assertEquals(priorProb["deNovoDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["deNovoAccPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refDonorPrior"], priorProbs["NA"])
        self.assertEquals(priorProb["refAccPrior"], priorProbs["NA"])
        # checks that de novo donor and acceptor flags are correct
        self.assertEquals(priorProb["deNovoDonorAltGreaterRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestRefFlag"], 0)
        self.assertEquals(priorProb["deNovoDonorAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoDonorFrameshiftFlag"], 0)
        self.assertEquals(priorProb["deNovoAccAltGreaterRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestRefFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccAltGreaterClosestAltFlag"], "N/A")
        self.assertEquals(priorProb["deNovoAccFrameshiftFlag"], "N/A")
        # checks that values are present for de novo donor and closest donor
        self.assertNotEquals(priorProb["refDeNovoDonorZ"], "N/A")
        self.assertNotEquals(priorProb["closestDonorRefMES"], "N/A")
        self.assertEquals(priorProb["closestDonorAltMES"], "N/A")
        # checks that splice positions are present for de novo and closest donor and NOT present for de novo and closest acceptor
        self.assertNotEquals(priorProb["deNovoDonorGenomicSplicePos"], "N/A")
        self.assertNotEquals(priorProb["closestDonorTranscriptSplicePos"], "N/A")
        self.assertEquals(priorProb["deNovoAccGenomicSplicePos"], "N/A")
        self.assertEquals(priorProb["closestAccTranscriptSplicePos"], "N/A")
        # checks that values are NOT present for de novo acceptor, closest acceptor, and ref donor and acceptor
        self.assertEquals(priorProb["altDeNovoAccMES"], "N/A")
        self.assertEquals(priorProb["closestAccRefZ"], "N/A")
        self.assertEquals(priorProb["closestAccAltZ"], "N/A")
        self.assertEquals(priorProb["refRefDonorSeq"], "N/A")
        self.assertEquals(priorProb["altRefAccSeq"], "N/A")
        # checks that all flags are equal to N/A
        self.assertEquals(priorProb["spliceRescue"], "N/A")
        self.assertEquals(priorProb["frameshiftFlag"], "N/A")
        self.assertEquals(priorProb["inExonicPortionFlag"], "N/A")
        self.assertEquals(priorProb["CIDomainInRegionFlag"], "N/A")
        self.assertEquals(priorProb["isDivisibleFlag"], "N/A")
        self.assertEquals(priorProb["lowMESFlag"], "N/A")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["sub"])
    def test_getVarDataNonACTG(self, getVarLocationSNS, getVarType):
        boundaries = "enigma"
        # the below is not the correct format for genome and transcript
        genome = "hg38"
        transcript = "NM_000059.3"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.4965C>R"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32339320"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "R"
        priorProb = calcVarPriors.getVarData(self.variant, boundaries, variantData, GENOME, BRCA1_RefSeq)
        self.assertEquals(priorProb["applicablePrior"], "-")

    @mock.patch('calcVarPriors.getVarLocationSNS', return_value = variantLocations["inExon"])
    @mock.patch('calcVarPriors.getVarType', return_value = varTypes["ins"])
    def test_getVarDataNonSNS(self, getVarLocationSNS, getVarType):
        boundaries = "enigma"
        self.variant["Gene_Symbol"] = "BRCA2"
        self.variant["Reference_Sequence"] = "NM_000059.3"
        self.variant["HGVS_cDNA"] = "c.4965delCinsGA"
        self.variant["Pos"] = self.variant["Hg38_Start"] = self.variant["Hg38_End"] = "32339320"
        self.variant["Ref"] = "C"
        self.variant["Alt"] = "GA"
        priorProb = calcVarPriors.getVarData(self.variant, boundaries, variantData, GENOME, BRCA2_RefSeq)
        self.assertEquals(priorProb["applicablePrior"], "-")
