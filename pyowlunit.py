from pyowlunit import TestSuite
import logging
import colorlog
import argparse

# TODO: Support file output
parser = argparse.ArgumentParser(description="Execute test according to Owl Unit ontology.")
parser.add_argument("-s", "--suite", metavar="suite", type=str, required=True,
                    help="IRI to the suite that will be executed or local file.")
parser.add_argument("-f", "--format", nargs="?", const="xml", metavar="format",
                    help="Format in which the tests have been serialized.")
args = parser.parse_args()

# Color results
logger = colorlog.getLogger()
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s[%(name)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# logger for pyowlunit executable
logger = colorlog.getLogger("pyowlunit")

try:
  ts = TestSuite(args.suite, format=args.format)
  ts.test()
except AssertionError as e:
  logger.critical(f"{e}")