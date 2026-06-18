# sources/storage-engines/foundationdb/layers/bulkload/bulk.py

Purpose: This Python 2 layer demonstrates a concurrent bulk-loading framework for moving external CSV, JSON, or blob data into FoundationDB key-value, SimpleDoc, or Blob-layer representations. It explicitly assumes the import has no atomicity or isolation requirement across the entire dataset.

Important APIs and types: `Subspace` wraps tuple prefixes; `BulkLoader` subclasses `gevent.queue.Queue` and defines `reader`, `writer`, and `produce_and_consume`. Reader classes are `ReadCSV`, `ReadJSON`, and `ReadBlob`; writer classes are `WriteKVP`, `WriteDoc`, and `WriteBlob`; combined classes include `CSVtoKVP`, `JSONtoDoc`, and `BlobToBlob`.

Control flow: Producers iterate `reader()` and enqueue transaction-sized data units while consumers dequeue and call transactional `writer` methods against the module-level gevent FDB database. CSV readers stream rows from matching files, JSON readers load one object per file with optional Unicode/number conversion, and blob readers yield `(offset, chunk)` pairs. Writers clear optional destinations, then write tuple-packed keys, SimpleDoc document updates, or blob chunks.

State and persistence behavior: Persistent state lives in FDB subspaces, SimpleDoc documents, and Blob-layer byte ranges. Queue state is in-memory and bounded by the consumer count to provide backpressure. Clearing is destructive for the configured destination subspace/document/blob.

Dependencies and integration points: The file uses `fdb.api_version(22)`, `fdb.open(event_model="gevent")`, `gevent`, `csv`, `json`, `blob`, and `simpledoc`. It is an example layer rather than a modern production loader.

Risks: It is Python 2 code (`print`, `xrange`, `unicode`, `iteritems`) and uses old API-version conventions. `WriteDoc.writer` calls `_writer_doc(db, ...)` rather than using the passed transaction, so composition expectations differ from plain `@fdb.transactional` methods. Tests should use temporary subspaces, verify row/chunk counts, clear behavior, JSON conversion, SimpleDoc array rejection, and gevent concurrency under retryable FDB errors.
