<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read_test.go -->
# sources/sync-backup/restic/internal/textfile/read_test.go

## Purpose
Tests textfile decoding and file reading across encodings.

## Important APIs and Control Flow
Helpers create temp files and decode hex fixtures. `TestRead` covers plain text, UTF-8 BOM, UTF-16 little/big endian BOMs, invalid/truncated inputs, and file read paths. Control flow writes fixtures, calls `Decode`/`Read`, and compares bytes or expected errors.

## State, Persistence, Dependencies, and Integration
State is temporary files and test byte slices. Dependencies include shared test helpers and encoding fixtures.

## Risks and Test Signals
The tests provide good coverage for BOM detection and decode errors, though not every possible Unicode normalization edge case.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read_test.go -->
