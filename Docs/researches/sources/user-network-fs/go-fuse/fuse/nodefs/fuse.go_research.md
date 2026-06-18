## sources/user-network-fs/go-fuse/fuse/nodefs/fuse.go

Purpose: convenience mounting functions for deprecated nodefs filesystems.

Important APIs/types/functions: `Mount` creates a `FileSystemConnector`, creates a `fuse.Server` from its raw FS, starts serving, waits for mount, and returns server/connector. `MountRoot` mounts with default raw mount options.

Control flow: build connector, mount server, launch serve goroutine, wait for mount readiness, then expose lifecycle objects to caller.

State and persistence: connector owns inode/file state; server owns kernel fd and mount lifecycle.

Dependencies and integration: nodefs equivalent of modern `fs.Mount`.

Risks and test signals: failure handling mirrors raw server mount behavior. Users must unmount to release kernel and connector state.
