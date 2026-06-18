# sources/user-network-fs/rclone/vfs/vfstest/fs.go

## Purpose
Provides the shared functional test harness for rclone VFS and mount tests.

## APIs, Flow, And State
`RunTests` iterates cache modes, writeback variants, and symlink variants, then runs the directory, file, read, write, edge-case, and symlink tests. `Run` stores the active `Oser`, VFS options, remote Fs, mount path, cleanup callback, and subprocess pipes. Helpers initialize random remotes, start direct VFS or mount subprocesses, normalize paths, compare local/remote trees, write/read files, create/remove dirs, symlink, check modes, and inspect mount/root.

## Dependencies And Integration
Depends on all rclone backends, `mountlib`, `fstest`, `walk`, VFS options, and the `submount.go` command channel. It is the central integration point for testing VFS behavior against both direct VFS APIs and real mounted filesystems.

## Risks And Test Signals
Global `run` makes tests sequentially coupled, and eventual-consistency retries can mask timing bugs while reducing flakes. The harness gives broad signal over cache mode regressions, permissions, directory listings, remote sync, and mount lifecycle.
