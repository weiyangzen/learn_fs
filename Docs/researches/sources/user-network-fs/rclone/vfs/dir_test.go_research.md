# sources/user-network-fs/rclone/vfs/dir_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_test.go -->
## sources/user-network-fs/rclone/vfs/dir_test.go

Purpose: broad unit/integration tests for VFS directory nodes and directory cache behavior.

Important APIs and control flow: helper `dirCreate` sets up a VFS with `dir/file1`. Tests cover basic node methods, `ForgetAll`, `ForgetPath`, cached directory walking, `SetModTime`, `Stat`, `ReadDirAll`, virtual adds/deletes, opening directories read-only, creating files, mkdir/submkdir, remove/remove-all/remove-name, file and directory rename, parent map key updates after `renameTree`, open-file virtual entries surviving forgets, directory modtime invalidation after writes, and metadata pseudo-file generation.

State, dependencies, and integration: tests use `fstest.Run`, backend operations, VFS cache/state, feature flags such as `CanHaveEmptyDirectories` and `DirModTimeUpdatesOnWrite`, runtime platform skips, JSON metadata parsing, and read-only option mutation.

Risks and test signals: this is a strong signal for user-visible VFS semantics and virtual-entry edge cases. It also documents known limitations, such as a newly created file not appearing in stat until opened for write. Coverage is environment-dependent for backend features and filesystem timestamp precision.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir_test.go -->
