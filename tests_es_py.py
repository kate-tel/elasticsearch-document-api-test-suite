import unittest
from elasticsearch import Elasticsearch, ConflictError, NotFoundError, RequestError
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk, BulkIndexError


class ElDocumentAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.es = Elasticsearch(
            [
                {'host': 'localhost', 
                'port': 9200}
                ]
            )

    def setUp(self):
        """
        Make sure all indices are deleted before each new test is run.
        """
        self.indices_client = IndicesClient(client=self.es)
        self.indices_client.delete(index='_all')

    def test_create_doc_with_id(self):
        '''Check that document is created'''
        expected_result = {
            '_index': 'twitter', 
            '_type': '_doc', 
            '_id': '1', 
            '_version': 1, 
            '_seq_no': 0, 
            '_primary_term': 1, 
            'found': True
        }
        self.es.create(
            index='twitter', 
            id=1,
            body={
                "user": "kimchy", 
                "twits": "1"
            }
        )
        self.assertEqual(
            self.es.get(
                index='twitter', 
                id=1,
                _source=False),
            expected_result)

    def test_create_existing_id(self):
        '''Check that a 409 response returns if document with existing ID is created'''
        self.es.create(
            index='twitter', 
            id=1,
            body={
                "user": "kimchy", 
                "twits": "1"
            }
        )
        with self.assertRaises(ConflictError):
            self.es.create(
            index='twitter', 
            id=1,
            body={
                "user": "japchae", 
                "twits": "1"
            }
        )

    def test_index_new_doc(self):
        ''' Check automatic ID generation. Generated ID is of type string '''
        doc = self.es.index(
            index='twitter', 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.assertIsInstance(
            doc['_id'], str)

    def test_index_existing_doc(self):
        ''' Unlike 'es.create', if the document already exists, updates the document and increments its version'''
        doc_seq_no_1 = self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )['_seq_no']
        doc_seq_no_2 = self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "japchae", 
                "twits": "1"
                }
            )['_seq_no']
        self.assertEqual(
            self.es.get_source(
                index='twitter', id=1
                ),
                {
                "user": "japchae", 
                "twits": "1"
                }   
        )

    def test_get_doc(self):
        '''Check that the specified JSON document is retrieved from an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.assertEqual(
            self.es.get(
                index='twitter',
                id = 1
        )['found'],
        True)

    def test_exists_doc(self):
        '''Check that the specified JSON document exists in an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.assertEqual(
            self.es.exists(
                index='twitter',
                id = 1
        ),
        True)

    def test_doc_not_found(self):
        '''Check that NotFoundError is returned if the requested document doesn't exist in an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        with self.assertRaises(NotFoundError):
                self.es.get(
                    index='twitter',
                    id = 2
            )

    def test_get_source(self):
        '''Check that the source of a JSON document is retrieved from an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.assertEqual(
            self.es.get_source(
                index='twitter',
                id = 1
        ),
        {
            "user": "kimchy", 
            "twits": "1"
                })

    def test_source_not_found(self):
        '''Check that NotFoundError is returned if the requested document doesn't exist in an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        with self.assertRaises(NotFoundError):
                self.es.get_source(
                    index='twitter',
                    id = 2
            )

    def test_delete_doc(self):
        '''Check that document is deleted from an index'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.es.delete(
            index='twitter', 
            id=1
            )
        self.assertEqual(
            self.es.exists(
                index='twitter', 
                id=1
            ), 
            False)

    def test_fail_delete_doc(self):
        '''Check that delete operation fails if no document with such ID'''
        self.es.index(
            index='twitter',
            id = 1, 
            body={
                "user": "kimchy", 
                "twits": "1"
                }
            )
        self.es.delete(
            index='twitter', 
            id=1
            )
        
        with self.assertRaises(NotFoundError):
            self.es.delete(
                index='twitter', 
                id=2
            )

    def test_delete_by_query(self):
        '''Check that document gets deleted by query. Refresh is set to 'true' to make created document visible to search'''
        self.es.index(
            index='rick&morty', 
            id=1, 
            body={
                'name': 'Rick'
            }, 
            refresh=True)
        q = {
            "query": {
                "match": {
                    "name": "Rick"
                }
            }
        }
        self.assertEqual(
            self.es.delete_by_query(
            index='rick&morty', 
            body=q
        )['deleted'],
        1)
        
    def test_fail_delete_by_query(self):
        '''Check that delete operation fails if query doesn't match any document'''
        self.es.index(
            index='rick&morty', 
            id=1, 
            body={
                'name': 'Rick'
            }, 
            refresh=True)
        q = {
            "query": {
                "match": {
                    "name": "Morty"
                }
            }
        }
        self.assertEqual(
            self.es.delete_by_query(
            index='rick&morty', 
            body=q
        )['deleted'],
        0)

    def test_update_doc_part(self):
        ''' Check that partial update adds a new field to the document'''
        self.es.index(
            index = 'rick&morty', 
            id = 1, 
            body = {
                'name': 'Rick'
            }, 
            refresh=True)
        self.es.update(
            index = 'rick&morty',
            id = 1,
            body = {
                "doc": {
                    "age": "25"
                    }
            }
        )
        self.assertIn(
            "age", 
            self.es.get_source(
                index = "rick&morty", 
                id = 1
                )
            )

    def test_update_doc_script(self):
        ''' Check that document is updated by a script'''
        self.es.index(
            index = 'rick&morty', 
            id = 1, 
            body = {
                'name': 'Morty'
            },  
            refresh = True
        )
        self.es.update(
            index = 'rick&morty',
            id = 1,
            body = {
                    "script" : "ctx._source.based_on = 'Marty McFly'"
            }
        )
        self.assertIn(
            "based_on", 
            self.es.get_source(
                index = "rick&morty", 
                id = 1
            )
        )

    def test_fail_update_doc_script(self):
        '''RequestError should be raised on invalid script update'''
        self.es.index(
            index = 'test', 
            id = 1, 
            body = {
                    "counter" : 1
            }, 
            refresh = True
        )
    
        with self.assertRaises(RequestError):
            self.es.update(
                index='test',
                id = 1,   
                body = {
                    "script": {
                        "age": "25"
                    }
                }
            )
                

    def test_update_by_query(self):
        '''Check that document gets updated by query. Refresh is set to 'true' to make created document visible to search'''
        self.es.index(
            index = 'test', 
            id = 1, 
            body = {
                "user" : "kimchy"
                }, 
            refresh = True
            )

        self.assertEqual(
            self.es.update_by_query(
                index='test', 
                body = {
                        "query": { 
                            "term": {
                            "user": "kimchy"
                            }
                        }
                    }
                )['updated'],
            1
        )

    def test_fail_update_by_query(self):
        '''NotFoundError should be raised if index doesn't exist'''
        
        with self.assertRaises(NotFoundError):
            self.es.update_by_query(
                index='test', 
                body = {    
                        "query": { 
                            "term": {
                            "user": "kimchy"
                            }
                        }
                    }
            )

    def test_mget(self):
        '''Check that multiple JSON documents are retrieved by ID.
        Order is specified in request.
        If there is a failure getting a particular document, the error is included in place of the document.'''
        
        self.es.create(
            index='rick&morty', 
            id=1, 
            body={
                'name': 'Rick'
                }
            )
        self.es.create(
            index='rick&morty', 
            id=2, 
            body={
                'name': 'Morty'
                }
            )
        body = {
            "docs": [
                {
                    "_id": "1"
                },
                {
                    "_id": "2"
                },
                {
                    "_id": "3"
                }
            ]
        }

        self.assertEqual(
            self.es.mget(
                body=body, 
                index="rick&morty"
                )['docs'][0]['found'],
                True)

        self.assertEqual(
            self.es.mget(
                body=body, 
                index="rick&morty",
                )['docs'][1]['found'], 
                True)

        self.assertEqual(
            self.es.mget(
                body=body, 
                index="rick&morty"
                )['docs'][2]['found'], 
                False)

    def test_bulk_index(self):
        '''Check API performs multiple indexing or delete operations in a single API call '''

        actions = [
                    {
                        '_op_type': 'index',
                        '_index': 'rick&morty',
                        '_id': 1,
                        '_source': {
                            'character': 'Rick'
                        }
                    },
                    {
                        '_op_type': 'delete',
                        '_index': 'rick&morty',
                        '_id': 1
                    }
        ]
    
        self.assertEqual(
                bulk(
                self.es, actions
                ),
                (2, [])
                )

    def test_bulk_fail(self):
        '''BulkIndexError is raised in if requested action fails to execute'''

        actions = [
                    {
                        '_op_type': 'index',
                        '_index': 'twitter',
                        '_id': 1,
                        '_source': {
                            'user': 'kimchy'
                        }
                    },
                    {
                        '_op_type': 'create',
                        '_index': 'twitter',
                        '_id': 1,
                        '_source': {
                            'user': 'japchae'
                        } 
                    }
        ]
        with self.assertRaises(BulkIndexError):
            self.assertEqual(
                    bulk(
                    self.es, actions
                    )
            )

    def test_reindex(self):
        '''Check that document is copied from one index to another'''
        
        self.es.index(
            index = 'twitter', 
            id = 1, 
            body = {
                'user':'kimchy'
                }, 
            refresh = True)

        self.es.reindex(
            body = {
                "source": {
                    "index": "twitter"
                },
                "dest": {
                    "index": "new_twitter"
                }
            }
        )

        self.assertEqual(
            self.es.get_source(
                index='twitter', 
                id=1
                ), 
            self.es.get_source(
                index='new_twitter', 
                id=1
                )
            )

    def test_reindex(self):
        '''Check that reindex cannot write into an index its reading from'''
        
        self.es.index(
            index = 'twitter', 
            id = 1, 
            body = {
                'user':'kimchy'
                }, 
            refresh = True)

        with self.assertRaises(RequestError):
            self.es.reindex(
                body = {
                    "source": {
                        "index": "twitter"
                    },
                    "dest": {
                        "index": "twitter"
                    }
                }
            )

    def test_temvestors(self):
        '''Checks that expected information and statistics for terms in the field of a document correspond actual'''

        self.es.create(
            index = 'client', 
            id = 1, 
            body = {
                "fullname": "John Doe",
                "text": "client test test test "
            }
        )
        self.es.create(
            index = 'client', 
            id = 2, 
            body = {
                "fullname": "Jane Doe",
                "text": "Another bank test ..."
            }
        )
        actual = self.es.termvectors(
            index = 'client', 
            id = 1, 
            body = {
                "fields": ["text"],
                "offsets": False,
                "positions": False,
                "term_statistics": True
            }
        )
        expected = {
            'term_vectors': {
                'text': {
                    'field_statistics': {
                        'sum_doc_freq': 5, 'doc_count': 2, 'sum_ttf': 7
                    }, 'terms': {
                        'client': {
                            'doc_freq': 1, 'ttf': 1, 'term_freq': 1
                        }, 'test': {
                            'doc_freq': 2, 'ttf': 4, 'term_freq': 3
                        }
                    }
                }
            }
        }

        subset = {k: v for k, v in actual.items() if k in expected}

        self.assertDictEqual(expected, subset)

    def test_temvestors_not_found(self):
        '''Response body contains 'found': 'False' if document is not present'''

        self.es.create(
            index = 'client', 
            id = 1, 
            body = {
                "fullname": "John Doe",
                "text": "client test test test "
            }
        )
        self.es.delete(index='client', id=1)

        self.assertEqual(
            self.es.termvectors(
            index = 'client', 
            id = 1, 
            body = {
                "fields": ["text"]
            }
        )['found'],
        False)

    def test_temvestors_invalid_field(self):
        ''' 'term_vectors' is an empty array if field is not present in a document'''

        self.es.create(
            index = 'client', 
            id = 1, 
            body = {
                "fullname": "John Doe",
                "text": "client test test test "
            }
        )
        
        self.assertEqual(
            self.es.termvectors(
            index = 'client', 
            id = 1, 
            body = {
                "fields": ["not_existing_field"]
            }
        )['term_vectors'],
        {})

    def test_mtermverctors(self):
        '''Checks the same as test_temvestors, but for multiple documents '''
        
        self.es.index(
            index='client', 
            id=1, 
            body={
                "fullname": "John Doe",
                "text": "client test test test "
            }
        )
        
        self.es.create(
            index='client', 
            id=2, 
            body={
                "fullname": "Jane Doe",
                "text": "Another bank test ..."
            }
        )

        response = self.es.mtermvectors(
            index='client', 
            body={
                "ids": ["1", "2"],
                "parameters": {
                    "fields": ["text"],
                    "offsets": False,
                    "positions": False
                    }
                }
            )
        terms_doc1 = {
                    'client': {
                        'term_freq': 1
                        }, 
                    'test': {
                        'term_freq': 3
                        }
                }
        terms_doc2 = {
                    'another': {
                        'term_freq': 1
                        }, 
                    'bank': {
                        'term_freq': 1
                        }, 
                    'test': {
                        'term_freq': 1
                        }
                }
        self.assertEqual(
            response['docs'][0]['term_vectors']['text']['terms'], 
            terms_doc1)
        self.assertEqual(
            response['docs'][1]['term_vectors']['text']['terms'], 
            terms_doc2)

    def test_mtermverctors_not_found(self):
        '''Response body contains 'found': 'False' if document is not present'''
        
        self.es.indices.create(
            index='twitter'
            )

        response = self.es.mtermvectors(
            index='twitter', 
            body={
                "ids": ["1", "2"],
                "parameters": {
                    "fields": ["text"]
                    }
                }
            )
        self.assertEqual(
            response['docs'][0]['found'],
            False)
        self.assertEqual(
            response['docs'][1]['found'],
            False)

    def test_mtemvestors_invalid_field(self):
        ''' 'term_vectors' is an empty array if field is not present in a document'''

        self.es.create(
            index = 'client', 
            id = 1, 
            body = {
                "fullname": "John Doe",
                "text": "client test test test "
            }
        )
        
        self.assertEqual(
            self.es.mtermvectors(
            index = 'client',  
            body = {
                "ids": ["1", "2"],
                "parameters": {
                    "fields": ["not_existing_field"]
                }
            }
            )['docs'][0]['term_vectors'],
        {})

if __name__ == '__main__':
    unittest.main(verbosity=2)
