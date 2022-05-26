import jpype
import jpype.imports
from jpype.types import *
from glob import glob
import os

CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.join(CUR_DIR_PATH, "..", "bin")

# initialize JVM
jpype.startJVM()

def load_jena():
  """
  Adds jena dependencies to JVM
  """
  jars_path = os.path.join(BIN_PATH, "jena", "*.jar")
  jars = glob(jars_path)

  for jar in jars:
    jpype.addClassPath(jar)

def load_owlapi():
  """
  Adds owlapi dependencies to JVM
  """
  jar_path = os.path.join(BIN_PATH, "owlapi-5.1.20.jar")
  jpype.addClassPath(jar_path)
