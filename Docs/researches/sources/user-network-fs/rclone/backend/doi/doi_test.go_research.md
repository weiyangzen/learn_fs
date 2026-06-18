# sources/user-network-fs/rclone/backend/doi/doi_test.go

Purpose: Hooks the DOI backend into rclone's generic integration test harness.

Important APIs, types, and functions: `TestIntegration` invokes `fstests.Run` with `RemoteName: "TestDoi:"` and `NilObject: (*Object)(nil)`.

Control flow: The test expects a configured `TestDoi:` remote and then lets fstests exercise standard filesystem behavior for the read-only DOI backend.

State and persistence behavior: Any state depends on the configured remote and provider. The backend itself remains read-only during these tests, so mutation tests should observe read-only errors.

Dependencies and integration points: Uses `fstest/fstests` and the package-local `Object` type. This is the external-service complement to `doi_internal_test.go`.

Risks: Without a configured remote, the test harness may skip or fail depending on fstests configuration. Generic tests may include mutation expectations that need backend read-only handling to be accepted.

Test signals: When configured, this provides broad compatibility coverage for listing, object reads, metadata, and expected unsupported write operations.
