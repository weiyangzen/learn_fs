# sources/user-network-fs/rclone/backend/oracleobjectstorage/oracleobjectstorage_test.go

Purpose: connects the Oracle Object Storage backend to rclone's standard integration test suite and exposes backend-specific upload/copy threshold setters for `fstests`.

Important APIs/types/functions: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestOracleObjectStorage:"`, storage tiers `standard` and `archive`, `NilObject: (*Object)(nil)`, and chunked upload minimum size. `SetUploadChunkSize`, `SetUploadCutoff`, and `SetCopyCutoff` delegate to unexported production setters. Compile-time assertions verify the `fstests` setter interfaces.

Control flow: `fstests.Run` drives all filesystem operations. When shared tests need to vary chunk or copy thresholds, they call the setter methods, receive the previous value, and can restore it later.

State and persistence: setter methods mutate only the in-memory `Fs.opt` fields. The integration test operates against the configured OCI remote, so remote buckets, objects, multipart uploads, and tier state may be created or changed during tests.

Dependencies/integration: depends on `github.com/rclone/rclone/fstest/fstests`, rclone `fs`, and backend constants/methods. It validates the production backend through rclone's common filesystem contract rather than mocking OCI.

Risks/test signals: tests require live OCI credentials, namespace, compartment, and permissions. Archive-tier testing can depend on OCI restore/tier semantics and may be slower or restricted. This file is the main test signal for end-to-end backend behavior and chunked upload configurability.
