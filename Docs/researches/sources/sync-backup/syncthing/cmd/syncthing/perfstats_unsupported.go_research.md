# sources/sync-backup/syncthing/cmd/syncthing/perfstats_unsupported.go

## Purpose
This small Go file supplies a no-op `startPerfStats` implementation for platforms where the Unix perf stats collector is not compiled: Solaris and Windows. It keeps the rest of the command code platform-neutral.

## Important APIs, Types, And Functions
The only function is `startPerfStats()`, with an empty body. Its signature matches the supported Unix implementation.

## Control Flow
There is no runtime control flow. If the binary is built with `solaris` or `windows` tags, calls to `startPerfStats` return immediately and no file is created.

## State And Persistence Behavior
The function performs no I/O, allocates no state, starts no goroutines, and persists nothing. This avoids relying on unsupported or differently shaped resource-accounting APIs on Solaris and Windows.

## Dependencies And Integration Points
The file is selected by `//go:build solaris || windows`. It integrates with `cmd/syncthing/main.go`, which can call `startPerfStats` without platform conditionals. The supported implementation lives in `perfstats_unix.go`.

## Risks And Edge Cases
Users enabling perf stats on Windows or Solaris get silent no-op behavior unless higher-level command help documents the platform limitation. Any future code expecting output files after calling `startPerfStats` must account for this build-specific no-op.

## Test Signals
The primary signal is successful compilation on Windows and Solaris targets. There are no direct tests because behavior is intentionally empty.
