# sources/user-network-fs/rclone/backend/box/box_test.go

## Purpose
Connects the Box backend to rclone's generic filesystem integration test suite.

## Important APIs, types, and functions
`TestIntegration` runs `fstests.Run` against `TestBox:` with nil `*box.Object`.

## Control flow
The generic fstests suite exercises standard filesystem operations against a configured Box remote through exported backend behavior because this file is in package `box_test`.

## State and persistence
No local persistent state. Test execution creates and removes data on the configured Box remote.

## Dependencies and integration points
Imports the Box backend and `fstests`. Requires external test configuration for `TestBox:`.

## Risks
Coverage is generic and does not directly target JWT auth, event polling, owner filtering, impersonation, multipart commit retries, conflict-copy workaround, or trash cleanup. Integration runs depend on account permissions, limits, and Box consistency.

## Test signals
Passing this test indicates the backend satisfies rclone's standard Fs/Object contract for the configured Box remote.
