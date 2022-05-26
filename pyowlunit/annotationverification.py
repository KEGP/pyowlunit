import rdflib
from rdflib.namespace import RDF
import json
from typing import Union
import logging
from pyowlunit.errors import AVViolation
import dictdiffer

import pyowlunit.utils.javabridge as jb
jb.load_jena()

from org.apache.jena.rdf.model import ModelFactory
from org.apache.jena.riot import RDFDataMgr
from org.topbraid.shacl.validation import ValidationUtil
from java.io import ByteArrayOutputStream
from java.lang import String

logger = logger = logging.getLogger('AV')

AV_DATA_QUERY = """
  PREFIX owlunit: <https://w3id.org/OWLunit/ontology/>
  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

  SELECT ?testedOntology
  WHERE {
      ?x owlunit:testsOntology ?testedOntology .
  }
  """

SHAPE_MESSAGE_EXTRACTION_QUERY = """
  PREFIX sh: <http://www.w3.org/ns/shacl#> 
  SELECT DISTINCT ?node ?message ?severity {
    ?vr a sh:ValidationResult .
    ?vr sh:focusNode ?node .
    ?vr sh:resultSeverity ?severity .
    ?vr sh:resultMessage ?message . 
  }
  """

class AnnotationVerification(object):
  """
  Represent an Owl Unit annotation verification test as a python object
  """
  def __init__(self, testuri: str, format: str = "xml"):
    """
    Initialize annotation verification test by loading the test
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
    av_graph = rdflib.Graph()
    self.format = format
    av_graph.parse(testuri, format=self.format)
    logger.debug("EP Graph parsed")

    av_data = av_graph.query(AV_DATA_QUERY)
    assert len(av_data) > 0, f"No error provocation test defined at uri {testuri}"
    assert len(av_data) == 1, f"More than one error provocation test defined at uri {testuri}"
    # extract query result
    av_data = list(av_data)[0]

    self.tested_ontology = str(av_data.testedOntology)
  
  def test(self) -> bool:
    """Execute test by loading the data and executing the SPARQL query.
    Response is deserialized and equality with expected response is checked.

    Raises:
        ValueError: TBD: Custom exceptions for error failing

    Returns:
        bool: True if the test didn't fail.
    """
    # Load tested ontology in jena
    ontologyModel = ModelFactory.createDefaultModel()
    RDFDataMgr.read(ontologyModel, self.tested_ontology)
    # etxract testedOntology base prefix, to avoid logging tests for imported ontologies 
    # (which might not satisfy the shapes ontology)
    testedOntologyBasePrefix = str(ontologyModel.getNsPrefixMap().get(""))
    # load shapes model in jena
    # TODO: Support additional shape graph
    shape_ontology_uri = "https://raw.githubusercontent.com/luigi-asprino/owl-unit/main/shapes/ontology.ttl"
    shapesModel = ModelFactory.createDefaultModel()
    RDFDataMgr.read(shapesModel, shape_ontology_uri)
    # validate the model using SHACL library
    validationResult = ValidationUtil.validateModel(ontologyModel, shapesModel, False)
    reportModel = validationResult.getModel()
    # serialize output to a string to get to python 
    modelOutputStream = ByteArrayOutputStream()
    reportModel.write(modelOutputStream)
    validatedResultOntology = str(String(modelOutputStream.toByteArray()))

    # load validated result ontology in rdflib
    shape_graph = rdflib.Graph()
    shape_graph.parse(data=validatedResultOntology, format="application/rdf+xml")
    errors = shape_graph.query(SHAPE_MESSAGE_EXTRACTION_QUERY)

    # filter out errors of other ontologies
    errors = filter(lambda x: str(x[0]).startswith(testedOntologyBasePrefix), errors)
    # remove IRI from entities
    remove_iri = lambda iri: iri.split("#")[-1] if "#" in iri else iri.split("/")[-1]
    errors = map(lambda x: (remove_iri(x[0]), str(x[1]), remove_iri(x[2])), errors)
    errors = list(errors)

    if len(errors) > 0:
      raise AVViolation(errors)

    return True

    
    
    


