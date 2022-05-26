import rdflib
from rdflib.namespace import RDF
import json
from typing import Union
import logging
import dictdiffer
import re
from pyowlunit.errors import InferenceVerificationError

import pyowlunit.utils.javabridge as jb
jb.load_jena()
jb.load_owlapi()

from org.apache.jena.rdf.model import ModelFactory
from org.apache.jena.query import QueryFactory, QueryExecutionFactory
from org.apache.jena.riot import RDFDataMgr

logger = logger = logging.getLogger('IV')

# TODO: Support different reasoners than HermiT (requires building owlapi again and adding reasoner dependencies or build it without reasoners and add the reasoner to bin/owlapi)
IV_DATA_QUERY = """
  PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

  SELECT ?testedOntology ?inputData ?sparqlQuery ?expectedResult
  WHERE {
      ?x owlunit:testsOntology ?testedOntology ;
         owlunit:hasInputData ?inputData ;
         owlunit:hasSPARQLUnitTest ?sparqlQuery ;
         owlunit:hasExpectedResult ?expectedResult .
  }
  """

class InferenceVerification(object):
  """
  Represent an Owl Unit inference verification test as a python object
  """
  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize inference verification test by loading the test
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
    iv_graph = rdflib.Graph()
    self.format = format
    iv_graph.parse(testuri, format=self.format)
    logger.debug("IV Graph parsed")

    av_data = iv_graph.query(IV_DATA_QUERY)
    assert len(av_data) > 0, f"No inference verification test defined at uri {testuri}"
    assert len(av_data) == 1, f"More than one inference verification test defined at uri {testuri}"
    # extract query result
    av_data = list(av_data)[0]

    self.tested_ontology = str(av_data.testedOntology)
    self.input_data = str(av_data.inputData)
    self.sparql_query = str(av_data.sparqlQuery)
    self.expected_result = bool(av_data.expectedResult)
  
  def test(self) -> bool:
    """Execute test by loading the data and executing the SPARQL query.
    Response is deserialized and equality with expected response is checked.

    Raises:
        ValueError: TBD: Custom exceptions for error failing

    Returns:
        bool: True if the test didn't fail.
    """
    # load tested ontology in jena
    ontologyModel = ModelFactory.createDefaultModel()
    RDFDataMgr.read(ontologyModel, self.tested_ontology)
    # load data in jena
    dataModel = ModelFactory.createDefaultModel()
    RDFDataMgr.read(dataModel, self.input_data)
    # merge ontologies
    ontology = ontologyModel.union(dataModel)

    query = QueryFactory.create(self.sparql_query)
    qexec = QueryExecutionFactory.create(query, ontology)
    result = qexec.execAsk()
    qexec.close()
    
    if result != self.expected_result:
      # extract ASK content
      ask_content = re.findall("ASK\s+\{(.*)\}", self.sparql_query)
      assert len(ask_content) > 0, "SPARQL query ASK clause is empty!"
      # TODO: Support more ask clauses
      ask_content = ask_content[0].strip()
      raise InferenceVerificationError(f"`{ask_content}` := {result} (expected {self.expected_result})")

    return result