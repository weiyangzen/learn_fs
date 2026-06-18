<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go

## Purpose
Go recipe example that stores a large logical value by splitting it into fixed-size chunks keyed by chunk offset.

## Important APIs, Types, And Functions
`write_blob`, `read_blob`, `CHUNK_SIZE`, and `main` using `directory.CreateOrOpen`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; write helpers split non-empty input into chunks and read helpers scan the blob subspace in key order and concatenate values.

## State And Persistence Behavior
Persistent state is one key per chunk in a blob subspace; callers must clear old chunks before overwriting with shorter data or stale chunks can remain.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/blob.go -->
