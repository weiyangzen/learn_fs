<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py

## Purpose
Python recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`to_tuples`, `from_tuples`, `insert_doc`, `_get_new_id`, `get_doc`, `print_subspace`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_doc.py -->
