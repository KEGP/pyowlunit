import rdflib
from pyowlunit.competencyquestion import CompetencyQuestionVerification
import logging

CQ_QUERY = """
PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?cq
WHERE {
    ?suite rdf:type owlunit:TestSuite ;
           owlunit:hasTestCase ?cq .
    ?cq rdf:type owlunit:CompetencyQuestionVerification .
}
"""

class TestSuite(object):
  """
  Represent an Owl Unit test suite as a python object
  """

  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize the test suite by loading the suite graph and 
    intializing all the testing tasks
    # TODO: Support other types of tests

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

    # extract competency questions
    cq_tests = self.suite_graph.query(CQ_QUERY)
    if len(cq_tests) > 0:
      self.competency_questions = [
        CompetencyQuestionVerification(str(x.cq), format=format) for x in cq_tests
      ]
    else:
      self.competency_questions = None
    self.passed_cq_tests = 0

  def test_competency_questions(self):
    """
    Run the competency questions and give feedback to the user by logging
    the results.
    """
    log = logging.getLogger("CQ")

    for cq in self.competency_questions:
      try:
        cq.test()
        log.info(f"{cq.competency_question} - PASSED")
        self.passed_cq_tests += 1
      except Exception as e:
        # TODO: Better error handling
        log.error(f"{cq.competency_question} - ERROR {e}")

  def test(self):
    """Run all tests"""
    log = logging.getLogger("SUITE")
    
    log.debug("Running CQ tests")
    self.test_competency_questions()
    log.warning(f"CQ: {self.passed_cq_tests}/{len(self.competency_questions)} passed")

    
