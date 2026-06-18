# sources/user-network-fs/rclone/backend/dropbox/dropbox_test.go

Purpose: This is the generic Dropbox backend integration-test entry point. It delegates most behavior checks to rclone's shared filesystem test suite.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestDropbox:"`, a nil `*Object`, and `ChunkedUploadConfig{MaxChunkSize: maxChunkSize}`. `Fs.SetUploadChunkSize` adapts the unexported `setUploadChunkSize` helper to the `fstests.SetUploadChunkSizer` interface.

Control flow: The shared test harness constructs the configured remote, runs standard object, directory, upload, move/copy, hash, and feature tests, and can adjust upload chunk size within backend constraints.

State and persistence behavior: The test mutates a real Dropbox test remote configured outside this file. The only local state is the temporary chunk-size override during selected tests.

Dependencies and integration points: It depends on `fstests`, a configured `TestDropbox:` remote, and backend support for `SetUploadChunkSizer`.

Risks: Coverage is mostly external to this file and depends on remote credentials, Dropbox API availability, and the generic test suite's expectations. Backend-specific export and path-length details are covered in `dropbox_internal_test.go`.

Test signals: Passing `fstests.Run` is the broad compatibility signal; chunked upload tests can exercise maximum chunk-size validation through the adapter.
