from typing import List, Tuple

class OwlUnitException(Exception):
  pass

class DeserializationError(OwlUnitException):
  """
  Exception to be used whenever a serialization reading error
  is encountered such as format mismatch or unsupported format.
  """
  pass

class ErrorProvocationFailure(OwlUnitException):
  """
  Exception to be used when an ErrorProvocation tests fails becuase
  the ontology is indeed consistent.
  """
  pass

class InferenceVerificationError(OwlUnitException):
  """
  Exception to be used when an InferenceVerification tests fails.
  """
  pass

class AVViolation(OwlUnitException):
  """
  This exception is used when a violation is found on annotation verification.
  """
  def __init__(self, violations: List[Tuple[str, str, str]]):
    """
    Args:
        differences (List[Tuple[str, str, str]]): List of violations in the form (node, message, severity)
    """
    self.viol = violations

  def __str__(self) -> str:
    """
    Build error string from found differences

    Returns:
        str: Error string built upon found differences
    """
    return "  ".join([f"`{node}` {severity}: {msg}\n" for node, msg, severity in self.viol])


class CQUnexpectedResponse(OwlUnitException):
  """
  This exception is used when an unexpected response have been found
  while checking a competency questions.
  """
  def __init__(self, differences: List[Tuple[str, str]]):
    """
    Args:
        differences (List[Tuple[str, str]]): List of tuples in the form (expected, found)
    """
    self.diff = differences

  def __str__(self) -> str:
    """
    Build error string from found differences

    Returns:
        str: Error string built upon found differences
    """
    return " - ".join([f"found `{found}` but `{expected}` was expected" for expected, found in self.diff])
