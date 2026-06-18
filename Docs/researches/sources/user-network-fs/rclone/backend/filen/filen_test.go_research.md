# sources/user-network-fs/rclone/backend/filen/filen_test.go

Purpose: This is the generic integration-test entry point for the Filen backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFilen:"` and `NilObject: (*Object)(nil)`.

Control flow: The shared rclone test suite constructs a Filen remote and exercises standard filesystem behavior.

State and persistence behavior: It mutates the configured Filen test remote, including encrypted files, directories, trash, and metadata.

Dependencies and integration points: It depends on `fstests`, the Filen backend, the Filen SDK, and configured credentials/API key.

Risks: Filen-specific chunk-writer concurrency, global trash cleanup, move rollback, and recursive listing helpers are not unit-tested here.

Test signals: Passing `fstests.Run` is the broad backend compatibility signal.
