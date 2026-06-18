# sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_others.go

## Purpose
Provides the non-Linux stub for inotify-limit error classification.

## Important APIs, Types, and Functions
`reachedMaxUserWatches(_ error) bool` always returns false.

## Control Flow
Non-Linux `BasicFilesystem.Watch` setup failures are returned as-is without Linux-specific FAQ rewriting.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Selected by `//go:build !linux` and used by `basicfs_watch.go`.

## Risks
Other platforms can have watch resource exhaustion errors, but this stub does not translate them into targeted guidance.

## Test Signals
No direct non-Linux test in this subset; behavior is intentionally trivial.
