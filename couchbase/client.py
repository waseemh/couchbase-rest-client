import requests
import json
from requests.auth import HTTPBasicAuth
from requests import exceptions

class CouchbaseClient:

    """
    Couchbase client instance, conforms to following REST API reference:
        https://docs.couchbase.com/server/5.1/rest-api
    """

    def __init__(self, protocol='http', host='localhost', port=8091, query_port=8093, username='Administrator', password='password'):
        """
        Initialize Couchbase client.
        :param protocol: couchbase HTTP connection protocol (default: http)
        :param host: couchbase host (default: localhost)
        :param port: couchbase port (default: 8091)
        :param query_port: couchbase query port (default: 8093) 
        :param username: administrator username (default: Administrator)
        :param password: administrator password (default: password)
        """
        self.protocol = protocol
        self.host = host
        self.port = port
        self.query_port = query_port
        self.username = username
        self.password = password

        self.base_url = '%s://%s:%s' % (self.protocol, self.host, self.port)
        self.query_url = '%s://%s:%s' % (self.protocol, self.host, self.query_port)

        self.session = requests.Session()

    @property
    def is_connected(self):
        """
        Check if connection to Couchbase cluster is valid.
        :return: true/false according to actual connection status
        """
        try:
            requests.get(url=self.base_url + '/pools', timeout=1)
        except exceptions.ConnectionError:
            return False
        except exceptions.Timeout:
            return False
        return True

    def init_cluster(self):
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        requests.post(url=self.base_url + '/node/controller/setupServices',
                      headers=headers,
                      data='services=kv,n1ql,index')
        requests.post(url=self.base_url + '/pools/default',
                      headers=headers,
                      data='memoryQuota=1024')
        requests.post(url=self.base_url + '/settings/web',
                      headers=headers,
                      data='username=%s&password=%s&port=SAME' % (self.username, self.password))
        # set default index storage mode (for performing index queries)
        requests.post(url=self.base_url + '/settings/indexes',
                      headers=headers,
                      data='storageMode=forestdb')

    def create_bucket(self, bucket_name, bucket_password, ram_quota_mb='256', proxy_port='11216', **kwargs):
        """
        Create Bucket with given name and password.
        :param proxy_port: 
        :param ram_quota_mb: 
        :param bucket_name: bucket name
        :param bucket_password: bucket password
        """
        request_data = {'name': bucket_name, 'ramQuotaMB': ram_quota_mb,
                        'authType': 'sasl', 'saslPassword': bucket_password,
                        'bucketType': 'couchbase', 'proxyPort': proxy_port}
        # update request data with optional arguments (according to REST API reference)
        request_data.update(kwargs)

        self._call_couchbase('POST', url=self.base_url + '/pools/default/buckets',
                             data=request_data)

    def get_bucket(self, bucket_name):
        """
        Get bucket information
        :param bucket_name: bucket name
        :return: bucket information dict
        """
        response = self._call_couchbase('GET', url=self.base_url + '/pools/default/buckets/' + bucket_name)
        return response.json()

    def edit_bucket(self, bucket_name, **kwargs):
        """
        Edit bucket parameters
        :param bucket_name: 
        :param kwargs: 
        """
        self._call_couchbase('POST', url=self.base_url + '/pools/default/buckets/' + bucket_name,
                             data=kwargs)

    def delete_bucket(self, bucket_name):
        """
        Delete bucket
        :param bucket_name: Bucket name
        """
        self._call_couchbase('DELETE', url=self.base_url + '/pools/default/buckets/' + bucket_name)

    def list_buckets(self):
        """
        List bucket
        :return: list of buckets data
        """
        response = self._call_couchbase('GET', url=self.base_url + '/pools/default/buckets')
        return response.json()

    def create_user(self, user_id, password, roles):
        """
        Create user with specific roles.
        :param user_id: user ID
        :param password: user password
        :param roles: list of user roles 
        """
        user_request_data = {'password': password, 'roles': roles}
        self._call_couchbase('PUT', url=self.base_url + '/settings/rbac/users/local/' + user_id,
                             data=user_request_data)

    def delete_user(self, user_id):
        """
        Delete user with given user_id
        :param user_id: user_id to delete
        """
        self._call_couchbase('DELETE', url=self.base_url + '/settings/rbac/users/local/' + user_id)

    def get_document(self, bucket_name, document_key):
        """
        Get document from bucket according to key.
        :param bucket_name: bucket name
        :param document_key: document key
        :return: dict of Document JSON
        """
        response = self._call_couchbase('GET', url=self.base_url + ('/pools/default/buckets/%s/docs/%s' % (bucket_name, document_key)),)
        return response.json()['json']

    def insert_document_from_file(self, bucket_name, document_key, document_file_path):
        """
        Read document content from file and insert it to bucket.
        :param bucket_name: bucket name
        :param document_key: document key
        :param document_file_path: path to document file
        """
        with open(document_file_path, 'r') as document_file:
            document_json = json.load(document_file)
        self.insert_document(bucket_name, document_key, document_json)

    def insert_document(self, bucket_name, document_key, document_json):
        """
        Insert document to bucket.
        :param bucket_name: bucket name
        :param document_key: document key
        :param document_json: document json dict
        """
        self._call_couchbase('POST', url=self.base_url + ('/pools/default/buckets/%s/docs/%s' % (bucket_name, document_key)),
                             data={"value": json.dumps(document_json)})

    def flush_bucket(self, bucket_name):
        """
        Flush bucket
        Reference: https://docs.couchbase.com/server/4.5/rest-api/rest-bucket-flush.html
        :param bucket_name: bucket name to flush
        """
        self._call_couchbase('POST', url=self.base_url + ('/pools/default/buckets/%s/controller/doFlush' % bucket_name),)

    def n1ql_query(self, query, positional_params=None, named_params=None):
        """
        Execute N1QL query. 
        N1QL query can be represented in following formats:
        1. statement with positional parameters:
              example: 'SELECT text FROM tweets WHERE rating = $1 AND when > $2'
          provide parameters as array according to their order in query
        2. statement with named parameters:
              example: 'SELECT text FROM tweets WHERE rating = $r AND when > $date'
          provide parameters as dictionary of parameters name and value (i.e: {"$r": 9.5,"$date": "1-1-2014"})
        3. statement with no parameters
        :param query: query string
        :param positional_params: list of positional parameters
        :param named_params: dict if named parameters
        :return: list of dicts of documents JSON
        """
        if positional_params is None:
            positional_params = []
        request_data = {'statement': query}
        if positional_params:
            request_data['args'] = positional_params
        elif named_params:
            for k, v in named_params.items():
                request_data[k] = v
        try:
            response = self._call_couchbase('POST', url=self.query_url + '/query/service',
                                            json=request_data)
            response_json = response.json()
            results = response_json['results']
            return results
        except:
            return None

    def _call_couchbase(self, method, url, **kwargs):
        # if data is present, add appropriate content-type header
        if 'data' in kwargs:
            headers = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        else:
            headers = None
        # HTTP Basic Auth using username and password
        auth = HTTPBasicAuth(self.username, self.password)
        # send request
        result = self.session.request(method, url, headers=headers, auth=auth, **kwargs)

        if not result.ok:
            raise CouchbaseApiException(result.text)

        return result

class CouchbaseApiException(Exception):
    pass
