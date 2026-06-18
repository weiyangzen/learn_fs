# sources/object-store/minio-mc/cmd/stat_test.go

## Purpose
Tests conversion from `ClientContent` to `statMessage`.

## Important APIs, types, and functions
- `TestParseStat` is table-driven over directory and file `ClientContent` examples.

## Control flow
For each case the test calls `parseStat`, checks metadata deep equality, size, optional expiry, file/folder type classification, and ETag quote trimming.

## State and persistence
No external state. Uses synthetic `ClientContent` values and client URLs.

## Dependencies and integration points
Targets `parseStat` from `stat.go`; uses Go `testing`, `reflect`, `strings`, `os`, and `time`.

## Risks and edge cases
- `targetAlias` is part of the test case struct but is unused.
- Does not check version ID, delete marker, expiration rule, restore info, checksums, or replication status.

## Test signals
Useful focused regression coverage for the basic object metadata normalization path.
