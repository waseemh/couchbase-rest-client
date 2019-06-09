# couchbase-rest-client

A lightweight couchbase REST client for Python 3.4 and above.

This library communicates with Couchbase REST API via HTTP, thus it is very easy to setup and does not require installing libcouchbase (C SDK) as in Couchbase Python SDK.

Client implementation conforms to [https://docs.couchbase.com/server/5.1/rest-api/rest-intro.html](official REST API reference).

Note that I follow the same recommendation given by Couchbase team that using the REST API for CRUD does not scale as well as SDKs and does not offer the same level of data protection.

However, REST API could be used for administrative tasks such as cluster maintenance, monitoring, statistics, temporary queries and is a perfect fit for integration/system tests involving Couchbase.

## Getting Started

### Initialize Couchbase client:
```python
from couchbase.client import CouchbaseClient
couchbase_client = CouchbaseClient()
```

### Create bucket:
```python
couchbase_client.create_bucket(bucket_name="mybucket", bucket_password="mypassword")
```

### Delete bucket:
```python
couchbase_client.delete_bucket(bucket_name="mybucket")
```

### Insert document to bucket:
```python
couchbase_client.insert_document(bucket_name="mybucket", document_key="mydocid", document_json={"foo": "bar"})
```

### N1QL queries:
Simple query: 
```python
couchbase_client.n1ql_query(query="SELECT text FROM tweets")
```

Query with positional parameters:
```python
couchbase_client.n1ql_query(query="SELECT text FROM tweets WHERE rating = $1 AND when > $2", positional_params=['9.5', '1-1-2014'])
```

Query with named parameters:
```python
couchbase_client.n1ql_query(query="SELECT text FROM tweets WHERE rating = $r AND when > $date", named_params={"$r": 9.5,"$date": "1-1-2014"})
```

All available methods are documented and can be found in module: ```couchbase/client.py```

## Tests

Tests assume that a local Couchbase instance is running.

**Docker** can be used to locally setup a Couchbase cluster for running tests. For example
```bash
docker run -p 8091-8093:8091-8093 -p 11210:11210 couchbase:community-5.1.1
```

Run tests using:
```bash
python setup.py test
```

## License

MIT
