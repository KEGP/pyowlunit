from pyowlunit import TestSuite
import logging

logging.basicConfig(format='[%(name)s - %(levelname)s] %(message)s', level=logging.INFO)
ts = TestSuite("https://raw.githubusercontent.com/luigi-asprino/owl-unit/main/examples/suite1.ttl", format="turtle")
ts.test()