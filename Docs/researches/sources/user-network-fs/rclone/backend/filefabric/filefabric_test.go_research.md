# sources/user-network-fs/rclone/backend/filefabric/filefabric_test.go

Purpose: This is the generic integration-test entry point for the Enterprise File Fabric backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFileFabric:"` and `NilObject: (*filefabric.Object)(nil)`.

Control flow: The shared rclone test suite constructs the configured remote and exercises standard filesystem behavior.

State and persistence behavior: It mutates the configured File Fabric remote and any token/version values the backend persists through its config mapper.

Dependencies and integration points: It depends on the backend package and `fstests`, plus a configured `TestFileFabric:` remote.

Risks: Provider version, token expiry, and background task timing may affect integration reliability. This file adds no unit-level coverage for File Fabric's custom authentication and upload flows.

Test signals: Passing `fstests.Run` is the broad compatibility signal.
