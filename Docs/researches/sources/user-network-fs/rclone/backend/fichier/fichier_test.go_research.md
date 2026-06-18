# sources/user-network-fs/rclone/backend/fichier/fichier_test.go

Purpose: This file is the generic integration-test entry point for the 1Fichier backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFichier:"`.

Control flow: The shared rclone test harness constructs the remote from configuration and runs standard filesystem behavior checks.

State and persistence behavior: It mutates the configured 1Fichier test remote and has no local state beyond the test harness.

Dependencies and integration points: It depends on `fstests` and a valid `TestFichier:` remote with suitable credentials.

Risks: There are no local unit tests for parsing retry error codes, upload finalization, or dircache behavior. Failures may reflect provider rate limiting, and `api.go` includes explicit flood sleep handling because integration tests can provoke it.

Test signals: Passing `fstests.Run` is the only signal in this file.
