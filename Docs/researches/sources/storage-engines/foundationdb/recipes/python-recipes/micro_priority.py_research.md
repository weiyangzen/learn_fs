<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py

## Purpose
Python recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`push`, `_next_count`, `pop`, `peek`, `clear_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_priority.py -->
