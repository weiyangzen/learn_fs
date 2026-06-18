<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go

## Purpose
Go recipe example that implements a priority queue ordered by tuple keys.

## Important APIs, Types, And Functions
`Priority.Push`, `_NextCount`, `Pop`, `Peek`, `_pack`, `_unpack`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; push writes `(priority, sequence, random)` keys, `peek` and `pop` scan one key from the front or back, and pop clears the selected key.

## State And Persistence Behavior
Persistent state is queue entries in priority order; sequence generation uses snapshot/range reads and random suffixes to reduce collisions.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/priority.go -->
