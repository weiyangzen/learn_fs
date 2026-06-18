# sources/sync-backup/syncthing/lib/fs/tempname_test.go

## Purpose
Tests and benchmarks temporary filename generation.

## Important APIs, Types, and Functions
`TestLongTempFilename`, `benchmarkTempName`, `BenchmarkTempNameShort`, and `BenchmarkTempNameLong`.

## Control Flow
The test creates a 300-character name, checks generated temp name length is bounded, and verifies short names retain the original basename plus `.tmp`. Benchmarks run `TempName` for short and long basenames under a sample directory.

## State and Persistence Behavior
No filesystem writes; only path string generation.

## Dependencies and Integration Points
Targets `TempName`.

## Risks
The length assertion is broad, not exact, which is fine for guarding the contract but does not pin platform-specific prefixes.

## Test Signals
Basic signal that temp names remain safe for long filenames and recognizable for short ones.
