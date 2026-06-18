# sources/user-network-fs/rclone/backend/netstorage/netstorage_test.go

## Purpose
`netstorage_test.go` runs the Akamai NetStorage backend through rclone's common integration suite. It validates backend conformance when a `TestnStorage:` remote is configured.

## Important APIs, Types, And Functions
The only test is `TestIntegration`, which calls `fstests.Run` with `RemoteName: "TestnStorage:"` and `NilObject: (*netstorage.Object)(nil)`.

## Control Flow
The shared harness constructs the backend, performs standard file and directory lifecycle operations, and checks optional interface behavior exposed by `netstorage.Fs`.

## State And Persistence Behavior
The test mutates the configured NetStorage account under the harness test root. It has no local fixtures or explicit cleanup beyond the shared harness.

## Dependencies And Integration Points
It imports `backend/netstorage` and `fstest/fstests`. The file is the primary automated signal that the signed HTTP backend works with rclone's common contract.

## Risks And Edge Cases
External NetStorage credentials, permissions, endpoint path, and service state determine whether the test can run. It does not isolate signing helpers, XML parsing, stat cache behavior, symlink conversion, or upload trailer construction.

## Test Signals
Passing integration tests indicate functional put/list/read/delete behavior. Focused unit tests would improve confidence in request signing and path/URL edge cases without needing Akamai service access.
