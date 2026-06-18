# sources/sync-backup/syncthing/lib/fs/casefs_test.go

## Purpose
Tests and benchmarks case-conflict detection over fake and real filesystems, including cache behavior under concurrent access.

## Important APIs, Types, and Functions
`TestRealCase`, `TestRealCaseSensitive`, `TestCaseFSStat`, `BenchmarkWalkCaseFakeFS100k`, `TestStressCaseFS`, `doubleWalkFS`, `doubleWalkFSWithOtherOps`, and `fakefsForTest`.

## Control Flow
Tests create mixed-case directory trees, query `realCase` with multiple spellings, and compare output to actual on-disk case. Stat tests distinguish underlying sensitive and insensitive filesystems. Benchmarks simulate scanner passes by walking and restatting paths. Stress tests run parallel walkers and touchers against a large fake FS with case conflict detection.

## State and Persistence Behavior
Uses fakeFS roots and real temp directories. Benchmarks and stress tests populate many in-memory fake entries and exercise shared case caches.

## Dependencies and Integration Points
Uses `OptionDetectCaseConflicts`, `NewFilesystem`, `UnicodeLowercaseNormalized`, `runtime`, and `testing.Short`.

## Risks
Real filesystem sensitivity detection can vary by platform and mount options. Stress test is skipped in short mode and timing-bound to ten seconds, so race coverage depends on CI settings.

## Test Signals
High confidence for case resolution correctness, case-sensitive behavior emulation, and cache concurrency under scanner-like workloads.
