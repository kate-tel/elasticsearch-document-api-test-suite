## **Elasticsearch Document API functional testing**

### **Table of Contents**

* [About this Project](#about-this-project)
* [Test coverage](#test-coverage)
* [Prerequisites](#prerequisites)
* [Setup of testing environment](#setup-of-testing-environment)
* [Running the tests](#running-the-tests)
* [References](#references)

### **About this Project**

This test suite perfoms functional testing for [ElasticSearch Document API 7.7.0](https://www.elastic.co/guide/en/elasticsearch/reference/7.7/docs.html).

### **Test coverage**

CRUD APIs covered by this test suite:

Single document APIs

* Index
* Get
* Delete
* Update

Multi-document APIs

* Multi get
* Bulk
* Delete by query
* Update by query API
* Reindex

### **Prerequisites**

1. [Python 3](https://www.python.org/downloads/)

### **Setup of testing environment**

1. Run Elasticsearch locally

This project is tested with Elasticsearch 7.7.0. Set up instructions can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/7.7/getting-started-install.html#run-elasticsearch-local).
For the purpose of running the test suite one-node cluster is enough. Follow steps 1-3. 
You now have a single-node Elasticsearch cluster up and running!

2. Clone this repository and go to folder

```bash
git clone https://github.com/kate-tel/elasticsearch-document-api-test-suite.git
cd elasticsearch-document-api-test-suite
```

3. Install virtualenv

```bash
pip3 install -U pip
pip3 install virtualenv
```

4. Create & activate virtual env

```bash
virtualenv .venv
source .venv/bin/activate
```

5. Install requirements. 

As a result, Python Elasticsearch Client 7.8.0 will be installed.

```bash
pip3 install -r requirements.txt
```

### **Running the tests**

1. To run the tests from the command line:

```bash
python -m unittest tests_es_py.py
```

2. To run individual test methods:

```bash
python -m unittest tests_es_py.ElDocumentAPITest.test_create_doc_with_id
```

### **References**

1. [Elasticsearch Document API documentation version 7.7.0](https://www.elastic.co/guide/en/elasticsearch/reference/7.7/docs.html).

2. [Python Elasticsearch Client API documentation](https://elasticsearch-py.readthedocs.io/en/master/api.html).

3. [Unittest Command-line interface for running the tests](https://docs.python.org/3/library/unittest.html#command-line-interface)