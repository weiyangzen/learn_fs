<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py

## Purpose
Python recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`_pack`, `_unpack`, `table_set_cell`, `table_get_cell`, `table_set_row`, `table_get_row`, `table_get_col`, `clear_subspace`.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_table.py -->
