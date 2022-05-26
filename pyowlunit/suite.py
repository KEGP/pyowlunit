import rdflib
from pyowlunit.competencyquestion import CompetencyQuestionVerification
from pyowlunit.errorprovocation import ErrorProvocation
from pyowlunit.annotationverification import AnnotationVerification
from pyowlunit.inferenceverification import InferenceVerification
import logging
from collections import defaultdict

TESTS_QUERY = """
PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?tc ?tcType
WHERE {
    ?suite rdf:type owlunit:TestSuite ;
           owlunit:hasTestCase ?tc .
    ?tc rdf:type ?tcType .
}
"""

class TestSuite(object):
  """
  Represent an Owl Unit test suite as a python object
  """
  TEST_CLASS_BIND = {
    "https://w3id.org/OWLunit/ontology/CompetencyQuestionVerification": CompetencyQuestionVerification,
    "https://w3id.org/OWLunit/ontology/ErrorProvocation": ErrorProvocation,
    "https://w3id.org/OWLunit/ontology/AnnotationVerification": AnnotationVerification,
    "https://w3id.org/OWLunit/ontology/InferenceVerification": InferenceVerification
  }

  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize the test suite by loading the suite graph and 
    intializing all the testing tasks
    # TODO: Support other types of tests
    # TODO: Support different level of annotation verification severity

    Args:
        testuri (str): URI of the test, a path to a local file
        # TODO: Support online resources
        format (str, optional): Format in which the graph have been serialized. Defaults to "xml".
                                See https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
                                for supported formats.
    """
    # build the inner graph containing the test suite
    self.suite_graph = rdflib.Graph()
    self.suite_graph.parse(testuri, format=format)

    self.tests = defaultdict(set)
    self.passed_tests = set()
    
    # extract tests
    extracted_tests = self.suite_graph.query(TESTS_QUERY)
    # more than one test is required
    assert len(extracted_tests) > 0, "Test suite is empty!"

    for uri, test_type in extracted_tests:
      if uri is not None:
        uri = str(uri)
        test_type = str(test_type)
        Cls = self.TEST_CLASS_BIND[test_type]
        self.tests[test_type].add(Cls(uri, format=format))
  
  def test_competency_questions(self):
    """
    Run the competency questions and give feedback to the user by logging
    the results.
    """
    log = logging.getLogger("CQ")

    for cq in self.tests["https://w3id.org/OWLunit/ontology/CompetencyQuestionVerification"]:
      try:
        cq.test()
        log.info(f"{cq.competency_question} - PASSED")
        self.passed_tests.add(cq)
      except Exception as e:
        # TODO: Better error handling
        log.error(f"{cq.competency_question} - ERROR {e}")

  def test_error_provocation(self):
    """
    Run the error provocation tests.
    """
    log = logging.getLogger("EP")

    for ep in self.tests["https://w3id.org/OWLunit/ontology/ErrorProvocation"]:
      try:
        ep.test()
        log.info(f"PASSED")
        self.passed_tests.add(ep)
      except Exception as e:
        # TODO: Better error handling
        log.error(f"ERROR")

  def test_annotation_verification(self):
    """
    Run the error provocation tests.
    """
    log = logging.getLogger("AV")

    for av in self.tests["https://w3id.org/OWLunit/ontology/AnnotationVerification"]:
      try:
        av.test()
        log.info(f"PASSED")
        self.passed_tests.add(av)
      except Exception as e:
        # TODO: Better error handling
        log.error(f"ERROR \n  {str(e).strip()}")

  def test_inference_verification(self):
    """
    Run the inference verification tests.
    """
    log = logging.getLogger("IV")

    for iv in self.tests["https://w3id.org/OWLunit/ontology/InferenceVerification"]:
      try:
        iv.test()
        log.info(f"PASSED")
        self.passed_tests.add(iv)
      except Exception as e:
        # TODO: Better error handling
        log.error(f"ERROR - {e}")

  def test(self):
    """Run all tests"""
    log = logging.getLogger("SUITE")
    
    log.debug("Running CQ tests")
    self.test_competency_questions()
    log.debug("Running EP tests")
    self.test_error_provocation()
    log.debug("Running AV tests")
    self.test_annotation_verification()
    log.debug("Running IV tests")
    self.test_inference_verification()

    log.warning(f"{len(self.passed_tests)}/{len(self.tests)} test passed.")
    
