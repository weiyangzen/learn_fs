<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py

## Purpose
Python recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`clear_subspace`, `write_blob`, `read_blob`, module-level `blob` subspace.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_blob.py -->
