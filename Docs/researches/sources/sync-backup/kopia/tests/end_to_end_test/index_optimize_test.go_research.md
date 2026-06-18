# sources/sync-backup/kopia/tests/end_to_end_test/index_optimize_test.go

## Purpose
Tests index optimization compacts multiple index blobs into one and that flush-per-source creates separate indexes.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestIndexOptimize`.

## Control Flow
The test creates a repo, skips if epoch manager is enabled, creates several snapshots to produce six indexes, runs `index optimize`, expects one index, then creates three sources with `--flush-per-source` and expects four indexes total.

## State and Persistence Behavior
Persists content indexes, compacts them, and writes new indexes on later flushes.

## Dependencies and Integration Points
Exercises repository status, snapshot creation, index listing, index optimize, and multi-source flush behavior.

## Risks
Hard-coded index counts depend on flush behavior and disabled epoch manager. The test skips a newer mode rather than validating equivalent behavior there.

## Test Signals
Shows index optimization reduces index count and flush-per-source adds one index per source.
