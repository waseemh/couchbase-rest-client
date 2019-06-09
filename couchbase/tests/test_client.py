import unittest
from couchbase.client import CouchbaseClient
import time

class TestCouchbaseClient(unittest.TestCase):

    def setUp(self):
        self.couchbase_client = CouchbaseClient()

    def test_create_bucket(self):
        self.couchbase_client.create_bucket("testbucket", "password123")
        self.couchbase_client.get_bucket("testbucket")

    def test_delete_bucket(self):
        self.couchbase_client.create_bucket("testbucket", "password123")
        self.couchbase_client.delete_bucket("testbucket")
        self.assertRaises(Exception, self.couchbase_client.get_bucket, "testbucket")

    def test_list_buckets(self):
        self.couchbase_client.create_bucket("testbucket1", "password123")
        self.couchbase_client.create_bucket("testbucket2", "password123", proxy_port=1129)
        buckets = self.couchbase_client.list_buckets()
        for bucket in buckets:
            assert bucket['name'] in ("testbucket1", "testbucket2"), "Unexpected bucket found"

    def test_insert_document(self):
        self.couchbase_client.create_bucket("testbucket", "password123")
        self.couchbase_client.insert_document("testbucket", "id123", {"key": "val"})
        assert self.couchbase_client.get_document("testbucket", "id123") == {"key": "val"}

    def tearDown(self):
        buckets = self.couchbase_client.list_buckets()
        for bucket in buckets:
            self.couchbase_client.delete_bucket(bucket['name'])
