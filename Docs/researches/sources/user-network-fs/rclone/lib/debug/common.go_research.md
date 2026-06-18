# sources/user-network-fs/rclone/lib/debug/common.go

## Purpose
This file exposes small wrappers around Go runtime debug knobs so rclone code can use package-local helpers for GC percentage and memory-limit changes.

## Important APIs, types, and functions
- `SetGCPercent(percent int) int` calls `runtime/debug.SetGCPercent`.
- `SetMemoryLimit(limit int64) int64` calls `runtime/debug.SetMemoryLimit`.

## Control flow
Both functions are direct pass-throughs returning the previous runtime setting from the Go runtime.

## State and persistence behavior
The functions mutate process-wide runtime settings. The changes last for the life of the process or until changed again; nothing is persisted to disk.

## Dependencies and integration points
The only dependency is the standard `runtime/debug` package. The wrappers are integration points for code that wants stable rclone-local symbols across Go versions.

## Risks and edge cases
These settings are global and can affect performance and memory use across the whole process. There is no validation or synchronization here; callers must supply sensible values.

## Test signals
No direct tests are present in this subset. Runtime behavior is inherited from the Go standard library.
