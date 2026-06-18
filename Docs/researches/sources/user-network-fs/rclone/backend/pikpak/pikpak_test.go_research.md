# sources/user-network-fs/rclone/backend/pikpak/pikpak_test.go

Purpose: connects the PikPak backend to rclone's integration test suite and exposes upload sizing controls.

Important APIs/types/functions: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestPikPak:"`, a nil object sentinel, and chunked upload min/max sizes. `SetUploadChunkSize` and `SetUploadCutoff` delegate to backend setters. Compile-time assertions verify the `fstests` setter interfaces.

Control flow: shared `fstests` drive behavior. Chunked upload tests can adjust backend chunk size and cutoff through the setter methods.

State and persistence: setters mutate in-memory options. Integration runs against the configured PikPak account and can create files, folders, trash entries, upload tasks, and shares.

Dependencies/integration: depends on rclone `fs`, `fstests`, and backend upload constants.

Risks/test signals: tests require valid credentials and may be sensitive to captcha, quota, task limits, throttling, or leftover remote tasks. Main signal is end-to-end rclone filesystem conformance plus chunk-size validation.
