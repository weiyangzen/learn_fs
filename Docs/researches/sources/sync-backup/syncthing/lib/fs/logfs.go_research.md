# sources/sync-backup/syncthing/lib/fs/logfs.go

## Purpose
Wraps a filesystem to log method calls, callers, arguments, results, and errors for debugging.

## Important APIs, Types, and Functions
`logFilesystem`, `newLogFilesystem`, `getCaller`, and overrides for most `Filesystem` methods including `Watch`, `Glob`, `Roots`, and `Usage`.

## Control Flow
Each method delegates to the embedded filesystem, then logs via `l.Debugln` with caller location, filesystem type/URI, operation name, arguments, and result/error. `underlying` supports wrapper unwrapping.

## State and Persistence Behavior
Stores the wrapped filesystem and caller-skip layer count. No persistent state.

## Dependencies and Integration Points
Constructed in `NewFilesystem` when `fs` or `walkfs` debug facilities are enabled. Works with `walkFilesystem` and caseFS layer counting.

## Risks
Logging can expose paths and operation arguments in debug logs and can add overhead. Caller depth must stay aligned with wrapper layering to identify useful call sites.

## Test Signals
No direct tests; behavior is validated by compilation and debug usage.
