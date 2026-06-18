<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/table.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/table.go

## Purpose
Go recipe example that implements a two-dimensional table with row and column indexes.

## Important APIs, Types, And Functions
`Table.NewTable`, `TableSetCell`, `TableGetCell`, `TableSetRow`, `TableGetRow`, `TableGetCol`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; set cell writes both row and column keys, row/column reads scan prefixes, and row replacement clears a row prefix before rewriting cells.

## State And Persistence Behavior
Persistent state duplicates cell values in row and column indexes, so mutations must update both indexes in one transaction.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/table.go -->
