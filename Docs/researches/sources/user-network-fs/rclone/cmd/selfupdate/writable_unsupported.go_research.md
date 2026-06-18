# sources/user-network-fs/rclone/cmd/selfupdate/writable_unsupported.go

## Purpose

This fallback makes the self-update writability probe permissive on Plan 9 and JavaScript builds.

## Important APIs, Types, and Functions

`writable(path string) bool` always returns true.

## Control Flow

The function intentionally performs no filesystem query. Any actual failure is deferred to the update write/replace operation.

## State and Persistence Behavior

No state or persistence is involved.

## Dependencies and Integration Points

Build tags are `(plan9 || js) && !noselfupdate`. It keeps the package buildable where the Unix and Windows probes do not apply.

## Risks and Test Signals

The permissive answer can show self-update as possible when the later write will fail. It is probably acceptable as a compatibility fallback, but there are no tests for Plan 9 or JS behavior here.
