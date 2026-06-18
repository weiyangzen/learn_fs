# sources/storage-engines/pebble/internal/manifest/blob_metadata_test.go

## Purpose
This file tests blob metadata parsing, latest-version blob-file tracking, blob lookup correctness, and lookup performance.

## Important APIs, Types, And Functions
`TestPhysicalBlobFile_ParseRoundTrip` and `TestBlobFileMetadata_ParseRoundTrip` verify debug string parsers. `TestCurrentBlobFileSet` drives `CurrentBlobFileSet` through datadriven commands. `TestBlobFileSet_Lookup`, `makeTestBlobFiles`, and `BenchmarkBlobFileSet_Lookup` validate and measure `BlobFileSet.Lookup`.

## Control Flow
Parse tests iterate table-driven inputs with optional whitespace, optional humanized sizes, and optional creation times. The datadriven test parses version edits, preserves `*TableMetadata` pointer identity across commands, initializes a `BulkVersionEdit`, applies version edits, and prints modified edits/current state/stats/candidates. Lookup tests build 10,000 physical blob files with some FileIDs mapping to different physical file numbers, then assert returned object file info.

## State, Persistence, And Side Effects
The tests keep mutable maps of table metadata to mimic version identity across datadriven operations. The datadriven fixture file `testdata/current_blob_file_set` is an external test dependency. Current time is simulated by a closure that advances by one second and logs timestamps, allowing deterministic age-heuristic testing.

## Dependencies And Integration Points
The file depends on `bytes`, `fmt`, `testing`, `time`, `datadriven`, Pebble `base`, and `testify/require`. It integrates debug parsers, version edit parsing, `BulkVersionEdit.Accumulate`, `CurrentBlobFileSet`, and B-tree-backed `BlobFileSet`.

## Risks And Edge Cases
Pointer identity is explicitly repaired after parsing because current blob references are keyed by `*TableMetadata`; forgetting this would make delete-reference tests invalid. Parse tests verify permissive formatting but not malformed inputs. Lookup tests cover many entries and replacement-style physical file numbers but not missing lookups or concurrent access.

## Test Signals
Passing tests signal that human debug formats round-trip, latest-version blob-file stats/rewrite state match datadriven expectations, and blob ID lookup returns the correct physical blob file at scale. The benchmark provides a read-path performance signal for manual B-tree lookup.
