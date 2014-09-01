#!/usr/bin/env python
'''Test of NI-DM SPM export tool

To run the test, copy the NIDM turtle file 'spm_nidm.ttl' obtained by exporting the 
results of example001 (as specified in 'examples/spm/example001') in a directory named 
spmexport' under 'test' and from the command line call:

python test/TestSPMResultDataModel.py 

@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>, Satrajit Ghosh
@copyright: University of Warwick 2014
'''
import unittest
import os
from subprocess import call
import re
import rdflib
from rdflib.graph import Graph

import sys
path = "./nidm/nidm/nidm-results/test"
sys.path.append(path)

from TestResultDataModel import TestResultDataModel
from TestCommons import *
from CheckConsistency import *

RELPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# FIXME: Extend tests to more than one dataset (group analysis, ...)
'''Tests based on the analysis of single-subject auditory data based on test01_spm_batch.m using SPM12b r5918.
'''
class TestSPMResultsDataModel(unittest.TestCase, TestResultDataModel):

    def setUp(self):
        self.my_execption = ""

        # Display log messages in console
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

        TestResultDataModel.setUp(self) 
        self.ground_truth_dir = os.path.join(self.ground_truth_dir, 'spm', 'example001')

        # Current module directory is used as test directory
        self.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spmexport', 'example001')
        
        # RDF obtained by the SPM export 
        self.spmexport = Graph()

        #  Turtle file obtained with SPM NI-DM export tool
        self.spm_export_ttl = os.path.join(self.test_dir, 'spm_nidm.ttl');
        # print "\n\nComparing: "+self.spm_export_ttl
        self.spmexport.parse(self.spm_export_ttl, format='turtle')

        # Retreive owl file for NIDM-Results
        self.owl_file = os.path.join(RELPATH, 'nidm', 'nidm', 'nidm-results', 'nidm-results.owl')

    def test01_class_consistency_with_owl(self):
        my_exception = check_class_names(self.spmexport, "SPM example001", owl_file=self.owl_file)

        # FIXME (error message display should be simplified when only one example...)
        if my_exception:
            error_msg = ""
            for unrecognised_class_name, examples in my_exception.items():
                error_msg += unrecognised_class_name+" (from "+', '.join(examples)+")"
            raise Exception(error_msg)

    def test02_attributes_consistency_with_owl(self):
        my_exception = check_attributes(self.spmexport, "SPM example001", owl_file=self.owl_file)

        # FIXME (error message display should be simplified when only one example...)
        error_msg = ""
        if my_exception[0]:
            for unrecognised_attribute, example_names in my_exception[0].items():
                error_msg += unrecognised_attribute+" (from "+', '.join(example_names)+")"
        if my_exception[1]:
            for unrecognised_range, example_names in my_exception[1].items():
                error_msg += unrecognised_range+" (from "+', '.join(example_names)+")"
        if error_msg:
            raise Exception(error_msg)

    '''Comparing that the ttl file generated by SPM and the expected ttl file (generated manually) are identical'''
    # FIXME: If terms PR is accepted then these tests should be moved to TestResultDataModel.py
    def test03_ex1_auditory_singlesub_full_graph(self):
        #  Turtle file of ground truth (manually computed) RDF
        ground_truth_provn = os.path.join(self.ground_truth_dir, 'example001_spm_results.provn');
        ground_truth_ttl = get_turtle(ground_truth_provn)

        # print "\n\nwith: "+ground_truth_ttl

        # RDF obtained by the ground truth export
        gt = Graph()
        gt.parse(ground_truth_ttl, format='turtle')

        self.compare_full_graphs(gt, self.spmexport)

        if self.my_execption:
            raise Exception(self.my_execption)

    # '''Test06: StatisticMap: existance and attributes'''
    # def test06_StatisticMap(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for: instance of type StatisticMap
    #     query = prefixInfo+"""
    #     SELECT ?smapid WHERE {
    #     }
    #     """

    #     res = self.spmexport.query(query)

    #     if not self.successful_retreive(res, 'StatisticMap'):
    #         raise Exception(self.my_execption)
       
    #     # If StatisticMap was found check that all the attributes are available for 
    #     # each StatisticMap entity
    #     for idx, row in enumerate(res.bindings):
    #         rowfmt = []
    #         for key, val in sorted(row.items()):
    #             logging.debug('%s-->%s' % (key, val.decode()))
    #             if not val.decode():
    #                 self.my_execption += "\nMissing: \t %s" % (key)
    #                 return False


    # '''Test02: Test availability of attributes needed to perform a meta-analysis as specified in use-case *1* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test02_metaanalysis_usecase1(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """
    #     # Look for:
    #     # - "location" of "Contrast map",
    #     # - "location" of "Contrast variance map",
    #     # - "prov:type" in "nidm" namespace of the analysis software.
    #     query = prefixInfo+"""
    #     SELECT ?cfile ?efile ?stype WHERE {
    #      ?aid a spm:contrast ;
    #           prov:wasAssociatedWith ?sid.
    #      ?sid a prov:Agent;
    #           a prov:SoftwareAgent;
    #           a ?stype . 
    #      FILTER regex(str(?stype), "nidm") 
    #      ?cid a nidm:contrastMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?cfile .
    #      ?eid a nidm:contrastStandardErrorMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?efile .
    #     }
    #     """

        # if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
        #     raise Exception(self.my_execption)

    # '''Test03: Test availability of attributes needed to perform a meta-analysis as specified in use-case *2* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test03_metaanalysis_usecase2(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - "location" of "Contrast map",
    #     # - "prov:type" in "nidm" namespace of the analysis software.
    #     query = prefixInfo+"""
    #     SELECT ?cfile ?efile ?stype WHERE {
    #      ?aid a spm:contrast ;
    #           prov:wasAssociatedWith ?sid.
    #      ?sid a prov:Agent;
    #           a prov:SoftwareAgent;
    #           a ?stype . 
    #      FILTER regex(str(?stype), "nidm") 
    #      ?cid a nidm:contrastMap ;
    #           prov:wasGeneratedBy ?aid ;
    #           prov:atLocation ?cfile .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)

    # '''Test04: Test availability of attributes needed to perform a meta-analysis as specified in use-case *3* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test04_metaanalysis_usecase3(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - "location" of "Statistic Map",
    #     # - "nidm:errorDegreesOfFreedom" in "Statistic Map".
    #     query = prefixInfo+"""
    #     SELECT ?sfile ?dof WHERE {
    #      ?sid a nidm:statisticalMap ;
    #           prov:atLocation ?sfile ;
    #           nidm:errorDegreesOfFreedom ?dof .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)

    # '''Test05: Test availability of attributes needed to perform a meta-analysis as specified in use-case *4* at: http://wiki.incf.org/mediawiki/index.php/Queries'''
    # def test05_metaanalysis_usecase4(self):
    #     prefixInfo = """
    #     prefix prov: <http://www.w3.org/ns/prov#>
    #     prefix spm: <http://www.fil.ion.ucl.ac.uk/spm/ns/#>
    #     prefix nidm: <http://nidm.nidash.org/>

    #     """

    #     # Look for:
    #     # - For each "Peak" "equivZStat" and"coordinate1" (and optionally "coordinate2" and "coordinate3"),
    #     # - "clusterSizeInVoxels" of "height threshold"
    #     # - "value" of "extent threshold"
    #     query = prefixInfo+"""
    #     SELECT ?equivz ?coord1 ?coord2 ?coord3 ?ethresh ?hthresh WHERE {
    #      ?pid a spm:peakStatistic ;
    #         prov:atLocation ?cid ;
    #         nidm:equivalentZStatistic ?equivz ;
    #         prov:wasDerivedFrom ?clid .
    #      ?cid a nidm:coordinate;
    #         nidm:coordinate1 ?coord1 .
    #         OPTIONAL { ?cid nidm:coordinate2 ?coord2 }
    #         OPTIONAL { ?cid nidm:coordinate3 ?coord3 }
    #      ?iid a nidm:inference .
    #      ?esid a spm:excursionSet;
    #         prov:wasGeneratedBy ?iid .
    #      ?setid a spm:setStatistic;
    #         prov:wasDerivedFrom ?esid .
    #      ?clid a spm:clusterStatistic;
    #         prov:wasDerivedFrom ?setid .
    #      ?tid a nidm:extentThreshold ;
    #         nidm:clusterSizeInVoxels ?ethresh .
    #      ?htid a nidm:heightThreshold ;
    #         prov:value ?hthresh .
    #     }
    #     """

    #     if not self.successful_retreive(self.spmexport.query(query), 'ContrastMap and ContrastStandardErrorMap'):
    #         raise Exception(self.my_execption)



if __name__ == '__main__':
    unittest.main()
