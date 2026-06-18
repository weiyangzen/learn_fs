# sources/user-network-fs/rclone/backend/drime/drime_test.go

Purpose: Integrates the Drime backend with rclone's generic filesystem test suite and exposes test-only upload tuning hooks.

Important APIs, types, and functions: `TestIntegration` calls `fstests.Run` for `TestDrime:` with `(*Object)(nil)` and minimum chunk size. `SetUploadChunkSize` and `SetUploadCutoff` forward to unexported setters. Interface assertions confirm the backend satisfies fstests upload tuning interfaces.

Control flow: The integration test uses the configured Drime remote and enables chunked upload testing with `minChunkSize`. Fstests can temporarily adjust chunk size and cutoff to force multipart paths.

State and persistence behavior: Test state lives on the configured Drime account and is managed by fstests. Setter methods mutate the live `Fs` options for the duration of tests.

Dependencies and integration points: Uses rclone `fs` size suffixes and `fstests`. It directly supports coverage of `OpenChunkWriter`, small uploads, and regular object operations in `drime.go`.

Risks: Requires real credentials/configuration, so CI coverage may be limited. There are no mocked tests for API error bodies, pagination, move/copy edge cases, or multipart abort behavior.

Test signals: When configured, passing fstests demonstrate listing, upload/download, deletion, directory handling, metadata basics, and chunked upload compatibility.
