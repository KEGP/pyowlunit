from typing import List, Tuple

class OwlUnitException(Exception):
  pass

class DeserializationError(OwlUnitException):
  """
  Exception to be used whenever a serialization reading error
  is encountered such as format mismatch or unsupported format.
  """
  pass

class CQUnexpectedResponse(OwlUnitException):
  """
  This exception is used when an unexpected response have been found
  while checking a competency questions.
  """
  def __init__(self, differences: List[Tuple]):
    """
    Args:
        differences (List[Tuple]): List of tuples in the form (expected, found)
    """
    self.diff = differences

  def __str__(self) -> str:
    """
    Build error string from found differences

    Returns:
        str: Error string built upon found differences
    """
    return " - ".join([f"found `{found}` but `{expected}` was expected" for expected, found in self.diff])
