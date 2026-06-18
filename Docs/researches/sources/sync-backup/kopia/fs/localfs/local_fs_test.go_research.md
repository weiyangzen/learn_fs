## sources/sync-backup/kopia/fs/localfs/local_fs_test.go

Purpose: validates public localfs behavior against the real temporary filesystem.

Important APIs/types/functions: `TestSymlink`, `TestFiles`, `TestIterate1000`, `TestIterate10`, `TestIterateNonExistent`, `verifyChild`, `TestLocalFilesystemPath`, `TestSplitDirPrefix`, and `TestIteratePermissionDenied`.

Control flow, state, and persistence: tests create temporary files, directories, symlinks, and permission states; wrap them through `Directory`/`NewEntry`; then inspect Kopia `fs` metadata and traversal results. Temporary filesystem state is cleaned up by test helpers.

Dependencies and integration points: tests use OS syscalls directly, `fs.GetAllEntries`, `fs.IterateEntries`, `testutil.TempDirectory`, and platform gates for Windows/root behavior.

Risks and test signals: strong signals for symlink resolution, missing directory errors, callback error propagation, path splitting, local path canonicalization, and permission-denied entries. Platform-specific build files still need coverage on their respective operating systems.
