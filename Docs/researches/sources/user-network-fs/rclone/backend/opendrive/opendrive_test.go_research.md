# sources/user-network-fs/rclone/backend/opendrive/opendrive_test.go

Purpose: provides the standard rclone integration test entry point for the OpenDrive backend.

Important APIs: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestOpenDrive:"` and `NilObject: (*opendrive.Object)(nil)`. The test package is `opendrive_test`, so it validates the public backend package boundary rather than internals.

Control flow: fstests creates the remote from configured test credentials, runs the generic filesystem behavior suite, and validates common operations such as put, list, open, remove, hashes, modtime, directory operations, and optional interfaces advertised by the backend.

State and persistence behavior: all state is in the configured live OpenDrive remote and whatever temporary files/directories fstests creates. This file has no local persistent state.

Dependencies and integration points: depends on `github.com/rclone/rclone/backend/opendrive` and `github.com/rclone/rclone/fstest/fstests`.

Risks: coverage is only as broad as generic fstests and requires a working `TestOpenDrive:` remote. It does not directly exercise edge cases visible in implementation, such as same-parent rename fallbacks, long-name truncation prevention, access levels, upload partial-write errors, or session expiration.

Test signals: confirms the backend conforms to rclone's generic filesystem contract under live credentials, but specialized behavior lacks targeted tests in this file.
