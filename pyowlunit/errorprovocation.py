import rdflib
from rdflib.namespace import RDF
from typing import Union
import logging
from pyowlunit import errors

import pyowlunit.utils.javabridge as jb
jb.load_owlapi()

from org.semanticweb.owlapi.apibinding import OWLManager
from org.semanticweb.owlapi.reasoner import SimpleConfiguration
from org.semanticweb.owlapi.model import IRI
from org.semanticweb.HermiT import ReasonerFactory

logger = logger = logging.getLogger('EP')

EP_DATA_QUERY = """
  PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

  SELECT ?inputData ?testedOntology
  WHERE {
      ?x owlunit:hasInputData ?inputData ;
         owlunit:testsOntology ?testedOntology .
  }
  """

class ErrorProvocation(object):
  """
  Represent an Owl Unit error provocation test as a python object
  """
  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize error provocation test by loading the test
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
    ep_graph = rdflib.Graph()
    self.format = format
    ep_graph.parse(testuri, format=self.format)
    logger.debug("EP Graph parsed")

    ep_data = ep_graph.query(EP_DATA_QUERY)
    assert len(ep_data) > 0, f"No error provocation test defined at uri {testuri}"
    assert len(ep_data) == 1, f"More than one error provocation test defined at uri {testuri}"
    # extract query result
    ep_data = list(ep_data)[0]

    # postpone input data loading to test execution to increase efficiency
    self.input_uri = str(ep_data.inputData)
    self.tested_ontology = str(ep_data.testedOntology)
  
  def test(self) -> bool:
    """Execute test by loading the data and executing the SPARQL query.
    Response is deserialized and equality with expected response is checked.

    Raises:
        ValueError: TBD: Custom exceptions for error failing

    Returns:
        bool: True if the test didn't fail.
    """
    # turn input ontology into IRI
    inputDataIRI = IRI.create(self.input_uri)
    # load ontology in owlapi lib
    ontologyManager = OWLManager.createOWLOntologyManager()
    owlOntology = ontologyManager.loadOntology(inputDataIRI)
    # build reasoner
    reasoner = ReasonerFactory().createReasoner(owlOntology, SimpleConfiguration())
    consistent = reasoner.isConsistent()

    if consistent is True:
      raise errors.ErrorProvocationFailure()
    
    return consistent
  

    
    
    


