<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py

## Purpose
Python recipe example that implements a FIFO queue on ordered tuple keys.

## Important APIs, Types, And Functions
`enqueue`, `dequeue`, `last_index`, `first_item`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. enqueue finds the last index with a snapshot reverse read and writes the next key with random tie-breaker where available; dequeue reads and clears the first item.

## State And Persistence Behavior
Persistent state is queue entries ordered by index; concurrent enqueue contention and empty queue behavior are example-level concerns.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_queue.py -->
