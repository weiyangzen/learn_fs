# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_test.go

Purpose: integration-tests the experimental NFS mount backend, including cache modes and subpath mounting.

Important functions/tests: `commandOK`, `TestMount`, and `TestSubpathMount`. `TestMount` checks passwordless sudo mount/umount where needed, iterates NFS handle cache types, configures env vars for subprocess mount, and runs `vfstest.RunTests`. `TestSubpathMount` mounts `/sub` from a local source and verifies `hello.txt` appears at mount root.

State/persistence: uses temp directories, environment variables, actual OS mounts, and global `sudo`/`mountPath` mutation with cleanup. Dependencies include system mount tools, capabilities for symlink cache, NFS server, VFS test harness. Risks are high environmental flakiness and privilege requirements. Test signal is broad but skipped in many setups.
