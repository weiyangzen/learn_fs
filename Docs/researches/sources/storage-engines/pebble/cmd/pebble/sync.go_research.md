<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/sync.go -->
# sources/storage-engines/pebble/cmd/pebble/sync.go

## Purpose
Defines `pebble bench sync <dir>`, a benchmark for synchronous writes or WAL-only writes.

## Important APIs, Types, and Functions
`syncConfig` is `bench.DefaultSyncConfig()`. `syncCmd` declares the command. `init` binds `--batch`, `--wal-only`, and `--values`. `runSync` installs a rate limiter and calls `bench.RunSync`.

## Control Flow
Cobra validates one directory argument, parses benchmark-specific and shared flags, then the runner delegates to `bench.RunSync`.

## State and Persistence Behavior
This wrapper stores in-memory config. Persistence and WAL behavior are performed by the benchmark implementation and depend on `--wal-only`, `--disable-wal`, `--wipe`, and related shared flags.

## Dependencies and Integration Points
Depends on Cobra and `bench.SyncConfig`. It uses `random.go` rate limiting and `main.go` shared benchmark config.

## Risks and Edge Cases
Contradictory durability flags are possible at the CLI layer and must be handled by `bench.RunSync`. `Run` cannot return an error to Cobra.

## Test Signals
No direct tests. Signals include batch/value distribution parsing, WAL-only mode behavior, and throughput pacing.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/sync.go -->
