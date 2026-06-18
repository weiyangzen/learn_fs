<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go

## Purpose
Go recipe example that models directed graph adjacency with forward and inverse indexes.

## Important APIs, Types, And Functions
`Graph.NewGraph`, `set_edge`, `del_edge`, `get_out_neighbors`, `get_in_neighbors`, `clear_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; edge setters write both forward and inverse keys, delete clears both, and neighbor reads scan the relevant prefix.

## State And Persistence Behavior
Persistent state duplicates each edge in two subspaces, so both writes must remain transactionally paired.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/graph.go -->
