**ElasticSearch Document API test suite using Python Elasticsearch Client**

This test suite perfoms functional testing for ElasticSearch Document API, which can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs.html). Elasticsearch is the distributed search and analytics engine for all types of data.

**About this Test Suite**

In this test suite I performed funtional testing of the following CRUD APIs:

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

To make Api calls using Python I used Python Elasticsearch Client 7.7.1 (Official low-level client for Elasticsearch).

Note:
Python Elasticsearch Client's `exists_source` object isn't included in the test suite due to bug.
This issue has been reported by me, see [issue](https://github.com/elastic/elasticsearch-py/issues/1270). The bug has been fixed on 03/06/2020, but hasn't been released yet (as of 05/06/2020). 

**Infranstructure**

1. Python 3
2. One-node Elasticsearch 7.7.0. cluster, running locally on machine.
3. Virtual environment.
4. Python Elasticsearch Client.

**Environment Setup**

1. Install Python 3

Detailed installation guide for various opeartion systems can be found [here](https://realpython.com/installing-python/).

2. Run Elasticsearch (ES) locally on your computer

Explicit guideline on ES installation can be found [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-install.html#run-elasticsearch-local). 
For the purpose of running the Test Suite (TS) one-node cluster is enough. Follow steps 1-3. 
You now have a single-node Elasticsearch cluster up and running!

3. Create a new virtual environment

Create a directory to neatly store the Test Suite in it.
```
$ mkdir <directory_name>
$ cd <directory_name>

```Create a virtual environment inside the folder.
```
$ python3 -m venv env

```
To activate a virtual environment, run from command line:
```
$ source env/bin/activate
```
To deactivate:
```
$ deactivate
```

4. Install Python Elasticsearch Client

Official low-level client for Elasticsearch. Its goal is to provide common ground for all Elasticsearch-related code in Python. Official documentation can be found [here](https://elasticsearch-py.readthedocs.io/en/master/index.html#).

Installation:
```
$ python -m pip install elasticsearch
```

5. Clone git repository

```
$ git clone https://github.com/kate-tel/elasticsearch-document-api-test-suite.git

```
This will create a folder `elasticsearch-document-api-test-suite` on your machine.

6. Run TS:
    - from the command line:
```
        $ python -m unittest elasticsearch-document-api-test-suite/tests_es_py.py

```    
    - or run in the Preferred Code editor (Sublime Text, Visual Studio Code etc.)