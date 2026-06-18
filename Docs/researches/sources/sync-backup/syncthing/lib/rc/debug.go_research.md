# sources/sync-backup/syncthing/lib/rc/debug.go

## Purpose
Defines the package logger adapter for the remote-control package.

## Important APIs, Types, and Functions
Package variable `l` is initialized with `slogutil.NewAdapter("Remote control package")`.

## Control Flow
There is no runtime control flow beyond package initialization.

## State and Persistence Behavior
The file creates an in-memory logger adapter. Logging output behavior depends on Syncthing's global logging configuration, not this file.

## Dependencies and Integration Points
Depends on `github.com/syncthing/syncthing/internal/slogutil`. `rc.go` uses `l` for debug logging in synchronization and event handling.

## Risks and Edge Cases
Logger name changes affect debug filtering and log interpretation. There are no direct functional risks.

## Test Signals
Compile-time package initialization is the only direct signal; rc integration tests exercise log calls indirectly.
