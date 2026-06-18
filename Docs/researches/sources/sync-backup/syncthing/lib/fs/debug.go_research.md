# sources/sync-backup/syncthing/lib/fs/debug.go

## Purpose
Defines the package logger adapter for filesystem access logging.

## Important APIs, Types, and Functions
Package variable `l = slogutil.NewAdapter("Filesystem access")`.

## Control Flow
No direct control flow. Other files call `l.Debugf`, `l.Debugln`, and `l.ShouldDebug` for conditional wrappers and diagnostics.

## State and Persistence Behavior
Logger state is owned by the shared logging system, not this file.

## Dependencies and Integration Points
Used by `filesystem.go`, `logfs.go`, `metrics.go`, `casefs.go`, `walkfs.go`, `basicfs_watch.go`, xattr code, and copy-range registration.

## Risks
Debug logging can change wrapper layering in `NewFilesystem` when `walkfs` or `fs` debug facilities are enabled, so logging configuration has minor behavioral/performance impact.

## Test Signals
No direct tests; logger use is indirectly exercised by package tests.
