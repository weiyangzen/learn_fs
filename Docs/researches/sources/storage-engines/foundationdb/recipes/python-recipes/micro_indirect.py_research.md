<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py

## Purpose
Python recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace.__enter__`, `__exit__`, `_update`, `current`, plus `clear_subspace`, `print_subspace`, `smoke_test`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_indirect.py -->
