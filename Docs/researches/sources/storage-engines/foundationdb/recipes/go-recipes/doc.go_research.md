<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go -->
# Research: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go

## Purpose
Go recipe example that maps nested JSON/document structures to tuple-addressed leaves.

## Important APIs, Types, And Functions
`ToTuples`, `FromTuples`, `Doc.InsertDoc`, `Doc.GetDoc`, `_GetNewID`, `clear_subspace`, `print_subspace`.

## Control Flow
`main` selects FoundationDB API version 800, opens the default database, creates/opens a directory or subspace, clears demo state where needed, performs a small smoke scenario, and prints results. Core operations run inside `Transact` or `ReadTransact`; conversion helpers flatten arrays/maps into path tuples, insert assigns or preserves `doc_id`, and retrieval scans a document prefix and reconstructs the object.

## State And Persistence Behavior
Persistent state is one key per document leaf under `(doc_id, path...)`; random ID allocation scans for collisions but is example-grade.

## Dependencies And Integration Points
Depends on the Go FoundationDB bindings (`fdb`, `directory`, `subspace`, `tuple`) and a reachable default cluster. These examples integrate with the recipe-book style API demonstrations rather than production packages.

## Risks And Edge Cases
Example code favors clarity over robustness: many errors are ignored or panicked, transaction conflicts are left to binding retries, and some type assertions are narrow. It should not be treated as a production library without stronger validation.

## Test Signals
The file contains an executable smoke test in `main`, but no automated assertion harness in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/recipes/go-recipes/doc.go -->
