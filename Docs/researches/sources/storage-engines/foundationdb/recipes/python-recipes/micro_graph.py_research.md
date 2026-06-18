<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py -->
# Research: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py

## Purpose
Python recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace` with `edge` and `inverse` subspaces.

## Control Flow
The module selects FoundationDB API version 300, opens the default database, defines transactional helpers with `@fdb.transactional`, and either runs a smoke test or leaves callable recipe functions. edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on legacy Python FoundationDB bindings and a default cluster; several files use Python 2 syntax (`print` statements, `iteritems`, `xrange`). These are tutorial recipes parallel to the Go/Java/Ruby examples.

## Risks And Edge Cases
Not production-hardened: examples clear fixed top-level subspaces, rely on old API version 300, and sometimes use Python 2 integer division or string/bytes behavior that differs on Python 3.

## Test Signals
Smoke-test code is inline in most files, but there are no formal tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/python-recipes/micro_graph.py -->
