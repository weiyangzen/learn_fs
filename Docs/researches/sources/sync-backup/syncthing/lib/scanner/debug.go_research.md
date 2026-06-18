# sources/sync-backup/syncthing/lib/scanner/debug.go

## Purpose
Defines the scanner package logger adapter.

## Important APIs, Types, and Functions
Package variable `l` is initialized with `slogutil.NewAdapter("File change detection and hashing")`.

## Control Flow
Only package initialization occurs.

## State and Persistence Behavior
In-memory logger adapter only. Actual log persistence is controlled by the application logging system.

## Dependencies and Integration Points
Depends on `internal/slogutil`. Scanner walk and hash code use `l` for debug messages about ignored files, hashing, normalization, and errors.

## Risks and Edge Cases
Changing the adapter string changes log filtering and diagnostics. No functional scanner behavior is implemented here.

## Test Signals
Compile coverage is sufficient; scanner behavior tests exercise code paths that call the logger indirectly.
