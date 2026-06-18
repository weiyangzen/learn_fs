# sources/user-network-fs/rclone/vfs/dir_handle_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle_test.go -->
## sources/user-network-fs/rclone/vfs/dir_handle_test.go

Purpose: tests VFS directory handle behavior.

Important APIs and control flow: `TestDirHandleMethods` opens a directory, checks `String` including nil cases, `Stat`, `Node`, and `Close`. `TestDirHandleReaddir` creates a directory with two files and a subdirectory, reads all entries at once, then reads in chunks of two and verifies final `io.EOF`. `TestDirHandleReaddirnames` smoke-tests name extraction.

State, dependencies, and integration: uses shared VFS test helpers, remote fixture writes, `os.O_RDONLY`, `io.EOF`, and testify. It verifies sorted listing inherited from `Dir.ReadDirAll`.

Risks and test signals: good coverage for cursor semantics. It does not test concurrent calls or directory changes after the handle snapshot is populated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_handle_test.go -->
