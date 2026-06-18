# sources/storage-engines/pebble/sstable/format_test.go

## Purpose
Tests table format parsing from footer tuple and conversion back to magic/version tuple.

## Important APIs, Types, and Functions
- `TestTableFormat_RoundTrip` enumerates valid LevelDB, RocksDBv2, and Pebble v1-v8 cases.
- Invalid cases cover bad RocksDB version, unsupported Pebble version, and unknown magic.

## Control Flow
Each case calls `parseTableFormat`, wraps errors to match reader footer errors, checks either exact error text or expected format, then checks `AsTuple`.

## State and Persistence Behavior
No persisted files are written; the test models footer magic/version interpretation.

## Dependencies and Integration Points
Uses `leaktest`, `errors.Wrapf`, `base.DiskFileNum`, and `require`. Provides a regression guard for reader footer parsing.

## Risks and Edge Cases
Exact error strings are asserted. New formats require adding valid cases and adjusting unsupported-version expectations.

## Test Signals
Strong targeted coverage for format tuple compatibility and corruption diagnostics.
