# sources/user-network-fs/rclone/backend/premiumizeme/premiumizeme_test.go

## Purpose
Defines the premiumize.me backend integration test entry point for rclone's standard `fstests` suite.

## Important APIs, Types, And Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestPremiumizeMe:"` and `NilObject: (*premiumizeme.Object)(nil)`. There are no local unit helpers or mocks.

## Control Flow
When the test remote is configured, the shared fstests harness creates the backend and exercises rclone filesystem behavior such as put, list, update, remove, directory handling, and optional features advertised by `premiumizeme.Fs`.

## State And Persistence
The test persists data only on the configured `TestPremiumizeMe:` remote during integration runs. It does not create local fixtures.

## Dependencies And Integration Points
Depends on `github.com/rclone/rclone/fstest/fstests` and the backend package. It is discovered by Go's test runner and relies on external credentials/config.

## Risks And Test Signals
Coverage is broad but only when integration credentials exist. It does not isolate retry, OAuth renewal, API-key shutdown, upload rollback, or case-insensitive conflict behavior with deterministic unit tests.
