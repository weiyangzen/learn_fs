<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go

## Purpose
Go recipe example that implements a multimap/multiset using atomic add counters.

## Important APIs, Types, And Functions
`MultiMap.NewMultiMap`, `MultiAdd`, `MultiSubtract`, `MultiGet`, `MultiGetCounts`, `MultiIsElement`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; add increments a tuple key, subtract decrements or clears at zero, and reads scan an index prefix for members and counts.

## State And Persistence Behavior
Persistent state stores little-endian counters by `(index, value)`; counter encoding and zero cleanup are correctness-sensitive.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/multi.go -->
