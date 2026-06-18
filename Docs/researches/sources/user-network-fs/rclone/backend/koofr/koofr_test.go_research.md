
# sources/user-network-fs/rclone/backend/koofr/koofr_test.go

## Purpose
Connects the Koofr backend to rclone's standard integration tests.

## Important APIs, Types, And Control Flow
`TestIntegration` invokes `fstests.Run` with `RemoteName: "TestKoofr:"`. The generic suite exercises the backend through rclone interfaces rather than direct helper calls.

## State And Persistence
Creates temporary remote test data in the configured Koofr account/mount and relies on the generic test harness for cleanup.

## Dependencies And Integration Points
Requires a configured `TestKoofr:` remote. This file intentionally imports only `fstests`, so concrete backend behavior is reached through backend registration elsewhere.

## Risks And Test Signals
Provides live end-to-end coverage but no unit-level isolation for provider defaults or error translation. Failures may come from network, credentials, account state, or backend regressions.
