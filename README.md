# pyowlunit

Python implementation of the Owl Unit testing suite.
Refer to the [official repository](https://github.com/luigi-asprino/owl-unit) for additional informations.

* **Only supports competency questions verification**
* Support for local and online ontologies

## Installation

```
pip install -r requirements.txt
```

## Usage
```
usage: pyowlunit.py [-h] -s suite [-f [format]]
```


## Example
```
> python pyowlunit.py -s examples/local/suite.ttl -f turtle
[CQ] What are the interests of a certain person? - PASSED
[EP] PASSED
[AV] ERROR 
  `RocketTopping` Warning: Classes should have at least one comment
  `Mushroom` Warning: Classes should have at least one comment
  `Capricciosa` Warning: Classes should have at least one comment
  .
  .
  .
[SUITE] 2/3 test passed.
```

```
> python pyowlunit.py -s https://raw.githubusercontent.com/KEGP/pyowlunit/main/examples/online/suite.ttl -f turtle
[CQ] What are the interests of a certain person? - PASSED
[EP] PASSED
[SUITE] 2/2 test passed.
```