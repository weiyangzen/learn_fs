# sources/sync-backup/syncthing/lib/fs/mtimefs_test.go

## Purpose
Tests virtual mtime preservation across stat, walk, open file stat, failed underlying timestamp calls, and case-insensitive paths.

## Important APIs, Types, and Functions
`TestMtimeFS`, `TestMtimeFSWalk`, `TestMtimeFSOpen`, `TestMtimeFSInsensitive`, `mapStore`, `failChtimes`, `evilChtimes`, `newMtimeFS`, and `newMtimeFSWithWalk`.

## Control Flow
Tests inject `chtimes` functions that succeed, fail, or set wrong truncated times, then verify `mtimeFS` still reports requested virtual times while underlying stats differ. Walk and open tests confirm wrapper ordering applies virtual times to traversal and file handles. Case-insensitive tests compare behavior with and without `WithCaseInsensitivity`.

## State and Persistence Behavior
Uses temp dirs and in-memory `mapStore` database. `evilChtimes` deliberately mutates disk mtimes differently from requested values.

## Dependencies and Integration Points
Exercises `NewFilesystem` with `NewMtimeOption`, unwrapping to `walkFilesystem` and `mtimeFS`, and platform case sensitivity assumptions.

## Risks
Case-insensitive test assumes Darwin/Windows filesystems are insensitive, which can be false on unusual mounts. DB errors are not represented by `mapStore`.

## Test Signals
Strong coverage for virtual mtime overlay semantics and wrapper integration.
