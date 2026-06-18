# sources/user-network-fs/rclone/vfs/errors_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors_test.go -->
## sources/user-network-fs/rclone/vfs/errors_test.go

Purpose: tests string rendering for custom VFS errors.

Important APIs and control flow: `TestErrorError` asserts `OK` renders as `Success`, `ENOSYS` as `Function not implemented`, and an unknown value as `Low level error 99`.

State, dependencies, and integration: dependencies are `testing` and testify. It is a direct enum string smoke test.

Risks and test signals: covers only rendering, not translation to platform mount error codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/errors_test.go -->
