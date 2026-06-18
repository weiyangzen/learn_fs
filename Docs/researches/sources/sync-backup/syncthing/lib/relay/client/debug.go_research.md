# sources/sync-backup/syncthing/lib/relay/client/debug.go

## Purpose
Defines the relay client package logger adapter.

## Important APIs, Types, and Functions
Package variable `l` is initialized with `slogutil.NewAdapter("Relay client")`.

## Control Flow
Only package initialization occurs.

## State and Persistence Behavior
The file holds in-memory logger state only. Log emission depends on callers in dynamic/static relay client code.

## Dependencies and Integration Points
Depends on `internal/slogutil`. `dynamic.go`, `static.go`, and `methods.go` use `l` for debug logging around relay lookup, connection, joining, messages, and errors.

## Risks and Edge Cases
Changing the adapter name affects log filtering. No functional behavior is present.

## Test Signals
Compile coverage is sufficient; relay client tests exercise log sites indirectly.
