<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py

## Purpose
Python recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`multi_add`, `multi_subtract`, `multi_get`, `multi_get_counts`, `multi_is_element`, timing helpers.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_multi.py -->
