# sources/user-network-fs/rclone/cmd/mount2/mount.go

Purpose: go-fuse v2 mount backend registered as hidden `mount2` command and RC mount type.

Important APIs: `mountOptions` builds `fuse.MountOptions`; `mount` validates mountpoint, builds `FS`, creates NodeFS/server, waits for mount readiness, and returns async error/unmount handles.

Control flow: options propagate allow-other/root, default permissions, read-only, idmapped mount, direct FUSE debug, max read-ahead/write, disabled xattrs and readdirplus. macOS-specific options set volume name and suppress Apple metadata files. `server.Serve` runs in a goroutine; `server.WaitMount` blocks until ready.

State/persistence: creates kernel FUSE mount and VFS state. Unmount shuts down VFS then calls `server.Unmount`. Dependencies are go-fuse v2, mountlib, VFS, runtime OS. Risks include unsupported writeback-cache, option differences versus bazil backend, server goroutine always sending nil, and hidden command behavior. Integration tests exercise it via `vfstest`.
