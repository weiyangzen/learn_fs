# sources/user-network-fs/rclone/backend/seafile/seafile_test.go

Purpose: external integration test entry point for the Seafile backend.

Important APIs/types/functions: `TestIntegration` invokes `fstests.Run` with `RemoteName: "TestSeafile:"` and `NilObject: (*seafile.Object)(nil)`.

Control flow: when the rclone test harness is configured with a `TestSeafile` remote, the generic filesystem test suite performs create, list, update, copy/move, delete, directory, and feature checks according to the backend's advertised capabilities. This file contains no backend logic itself.

State and persistence behavior: all persistent effects are on the configured live Seafile remote and the rclone test framework. The test relies on external configuration and credentials.

Dependencies/integration: imports the backend package as an external consumer and `github.com/rclone/rclone/fstest/fstests`. This verifies public interface conformance rather than private helper behavior.

Risks/test signals: broad live coverage is valuable for API drift, auth, library handling, and object operations, but it is environment-dependent and not deterministic in ordinary unit runs. It does not isolate specific failure paths; those require targeted unit tests or mocked REST tests.
