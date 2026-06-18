# sources/storage-engines/pebble/sstable/testdata/Makefile

## Purpose
Defines fixture regeneration targets for SSTable testdata.

## Important APIs, Types, And Functions
Targets are `all`, `.PHONY: rebuild`, `rebuild`, and `h.txt`. `rebuild` runs `go run ./make-table.go`. `h.txt` derives word counts from `hamlet-act-1.txt`.

## Control Flow
The `h.txt` pipeline lowercases Hamlet text, extracts words, sorts, counts unique words, formats count/key rows, and writes `h.txt`. Rebuild then invokes the Go fixture generator.

## State And Persistence Behavior
Persists regenerated `h.txt` and SST fixture files under `sstable/testdata`.

## Dependencies And Integration Points
Used with `make-table.go`, fixture metadata in `test_fixtures.go`, and standard Unix text tools (`cat`, `tr`, `grep`, `sort`, `uniq`, `awk`).

## Risks And Edge Cases
The pipeline depends on locale/tool behavior for word extraction and sorting. Regenerated fixture bytes can change if writer, compression, or input text changes.

## Test Signals
Successful `make rebuild` and matching fixture tests indicate consistency.
