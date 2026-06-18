# sources/user-network-fs/rclone/cmd/mount/mount.go

Purpose: Linux-only bazil FUSE backend for `rclone mount`.

Important APIs: `init` registers the visible `mount` command and RC mount type; `mountOptions` converts `mountlib.Options` and VFS options to bazil `fuse.MountOption`s; `mount` performs overlap/non-empty checks, mounts, starts the server goroutine, and returns async error/unmount handles.

Control flow: rejects overlapping local source/mount paths and non-empty mountpoints unless allowed, enables FUSE debug callback, calls `fuse.Mount`, creates `FS` and bazil server, serves in a goroutine, and closes the connection when serving ends. Unmount shuts down VFS before `fuse.Unmount`.

State/persistence: creates a kernel mount and VFS cache state; unmount tears both down. Dependencies are bazil fuse, mountlib lifecycle, and VFS. Risks include unsupported `--allow-root`, ignored `-o/--option` and `--fuse-flag`, serve goroutine error handling, and platform-specific FUSE behavior.
