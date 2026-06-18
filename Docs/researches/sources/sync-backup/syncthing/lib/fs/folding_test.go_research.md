# sources/sync-backup/syncthing/lib/fs/folding_test.go

## Purpose
Verifies Unicode case folding and normalization behavior used for filesystem case-insensitive comparisons.

## Important APIs, Types, and Functions
`caseCases`, `benchmarkCases`, `TestUnicodeLowercaseNormalized`, and `BenchmarkUnicodeLowercase`.

## Control Flow
The test iterates representative strings and compares `UnicodeLowercaseNormalized` output to expected canonical forms. Benchmarks measure allocations and speed for ASCII, Latin-1, and mixed Unicode names.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Targets `folding.go`; indirectly protects caseFS, fakeFS insensitive mode, Windows path handling, and mtime insensitive storage.

## Risks
The expected outputs encode deliberate choices for tricky language cases. Any change to folding semantics can affect conflict detection and path matching.

## Test Signals
Good coverage of the Unicode edge cases Syncthing relies on for portable case folding.
