## sources/user-network-fs/go-fuse/fs/mount.go

Purpose: convenience entry point that mounts a high-level `fs` inode tree and starts serving it.

Important APIs/types/functions: `Mount(dir string, root InodeEmbedder, options *Options) (*fuse.Server, error)` calls `NewNodeFS`, passes `options.MountOptions` into `fuse.NewServer`, launches `server.Serve()` in a goroutine, waits with `WaitMount`, and returns the server.

Control flow: construct raw bridge, create server, start serving, wait for mount completion. If mount creation or waiting fails, the error is returned; the failed serve loop is expected to exit naturally.

State and persistence: it owns no filesystem state directly, but wires `Options` into both high-level FS behavior and kernel mount options. The returned server controls lifecycle and unmount.

Dependencies and integration: integrates the `fs` package with the raw `fuse.Server`. This wrapper is used by examples and most `fs` tests.

Risks and test signals: callers must call `Unmount`/`Wait` to clean up. Errors after `Serve` starts rely on the server loop exiting; tests around parallel mount and basic mount lifecycle exercise this path.
