<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go -->
# sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go

Purpose: example FUSE filesystem exposing a `clock` file whose content changes every second and invalidates kernel cache data.

Important APIs, types, and functions: defines `FS`, `Dir`, and `File`; uses `fuse.Mount`, `fs.New`, `Server.InvalidateNodeData`, `atomic.Value`, `OpenKeepCache`, and `fuseutil.HandleRead`.

Control flow: `run` mounts, creates a server and persistent clock node, ticks once, starts an update goroutine, and serves. Directory lookup returns the clock file; file open allows read-only access and read returns current content.

State and persistence behavior: file content and update count are in memory only. Kernel cache state is invalidated on every tick.

Dependencies and integration points: demonstrates bazil/fuse fs interfaces, mount options, and notification APIs.

Risks and test signals: update goroutine never exits in the example. Cache invalidation may return `ErrNotCached`, which is ignored; visible signal is changing file content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/examples/clockfs/clockfs.go -->
