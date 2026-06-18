<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go

## Purpose
Go recipe example that demonstrates directory-layer indirection for atomic workspace replacement.

## Important APIs, Types, And Functions
`Workspace.GetCurrent`, `Workspace.Session`, `_Update`, `clear_subspace`, `print_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; a workspace writes to a `new` directory and then removes `current` and moves `new` to `current` inside a transaction.

## State And Persistence Behavior
Persistent state is directory-layer metadata plus data under current/new directories; failures before the move leave old current intact.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/indirect.go -->
