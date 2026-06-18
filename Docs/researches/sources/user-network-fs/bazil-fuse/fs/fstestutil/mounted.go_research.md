<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go

Purpose: test helper for mounting a FUSE filesystem in a temporary directory and serving it in a goroutine.

Important APIs, types, and functions: defines `Mount`, `Close`, `MountedFunc`, `Mounted`, `MountedFuncT`, and `MountedT`.

Control flow: `MountedFunc` creates a temp dir, mounts FUSE, constructs an `fs.Server`, starts `server.Serve` in a goroutine, and returns a `Mount`. `Close` retries unmount, waits for serve completion, closes the connection, and removes the directory.

State and persistence behavior: owns temporary mount directory, FUSE connection, server, error channel, and closed flag.

Dependencies and integration points: used by tests and benchmarks; integrates `fuse.Mount`, `fuse.Unmount`, `fs.New`, and optional testing debug logs.

Risks and test signals: unmount can be busy and is retried up to 1000 times. Tests rely on proper cleanup to avoid leaked mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/mounted.go -->
