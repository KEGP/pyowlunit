import rdflib
import json
from typing import Union
import logging
from pyowlunit import errors
import dictdiffer

logger = logger = logging.getLogger('CQ')

CQ_DATA_QUERY = """
  PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

  SELECT ?inputData ?sparqlQuery ?expectedResult ?competencyQuestion
  WHERE {
      ?x owlunit:hasInputData ?inputData ;
        owlunit:hasSPARQLUnitTest ?sparqlQuery ;
        owlunit:hasExpectedResult ?expectedResult ;
        owlunit:hasCompetencyQuestion ?competencyQuestion .
  }
  """

class CompetencyQuestionVerification(object):
  """
  Represent an Owl Unit competency question test as a python object
  """
  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize competency question verification by loading the competency question
    graph and its information. Data loading is postponed to the instant in which
    the test is actually executed.

    Args:
        testuri (str): URI of the test, a path to a local file
        # TODO: Support online resources
        format (str, optional): Format in which the graph have been serialized. Defaults to "xml".
                                See https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph.parse
                                for supported formats.
    Raises:
        ValueError: TBD: Custom exception for error handling
    """
    # build the inner graph containing the test competency question
    self.cq_graph = rdflib.Graph()
    self.cq_graph.parse(testuri, format=format)
    logger.debug("CQ Graph parsed")

    cq_data = self.cq_graph.query(CQ_DATA_QUERY)
    assert len(cq_data) == 1, f"More than one competency question defined at uri {testuri}"
    # extract query result
    cq_data = list(cq_data)[0]

    # parse cq test content
    self.competency_question = str(cq_data.competencyQuestion)
    self.sparql_test_query = str(cq_data.sparqlQuery)

    # parse expected result as an actual JSON
    # TODO: Is this always a JSON? Can we check that?
    try:
      self.expected_result = json.loads(str(cq_data.expectedResult))
    except:
      raise ValueError("Expected result is not a valid JSON!")

    # postpone input data loading to test execution to increase efficiency
    self.input_uri = str(cq_data.inputData)
  
  def test(self) -> bool:
    """Execute test by loading the data and executing the SPARQL query.
    Response is deserialized and equality with expected response is checked.

    Raises:
        ValueError: TBD: Custom exceptions for error failing

    Returns:
        bool: True if the test didn't fail.
    """
    cq_data = rdflib.Graph()
    cq_data.parse(self.input_uri)

    # execute query
    result = cq_data.query(self.sparql_test_query)
    # serialize result into json and parse it into python dict
    # TODO: This should be dependant on the expected result format
    result = json.loads(result.serialize(format="json"))

    # TODO: Improve error comunication
    if result == self.expected_result:
      return True
    else:
      # TODO: Custom exception
      differences = list()
      for type, path, d in dictdiffer.diff(self.expected_result, result):
        # TODO: Support also add and remove
        if type == "change":
          path = "/".join([str(p) for p in path])
          found, expected = d
          differences.append((f"{path}/{expected}", f"{path}/{found}"))
          
      raise errors.CQUnexpectedResponse(differences)
  

    
    
    


