from pyowlunit import TestSuite
import logging

logging.basicConfig(format='[%(name)s - %(levelname)s] %(message)s', level=logging.INFO)
ts = TestSuite("/home/n28div/university/knowledge-engineering/exam-project/owntestingtool/examples/local/suite.ttl", format="turtle")
ts.test()