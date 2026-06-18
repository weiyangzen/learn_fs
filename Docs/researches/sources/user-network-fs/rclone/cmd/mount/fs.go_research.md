# sources/user-network-fs/rclone/cmd/mount/fs.go

Purpose: Linux-only top-level bazil FUSE filesystem wrapper around rclone VFS.

Important APIs/types: `FS` contains `*vfs.VFS`, underlying `fs.Fs`, `*mountlib.Options`, and bazil server pointer. `NewFS`, `Root`, `Statfs`, and `translateError` are the key functions.

Control flow: `Root` obtains the VFS root directory and wraps it in a `Dir`. `Statfs` maps VFS capacity to FUSE block stats and clips platform-limited block counts via `mountlib.ClipBlocks`. `translateError` maps VFS/rclone sentinel errors to errno values and logs unknown I/O errors.

State/persistence: owns references to live VFS and FUSE server but no persistent data. Dependencies are bazil fuse, rclone `fserrors`, `vfs`, and mountlib. Risks are incomplete error mapping and capacity values derived from remotes with unknown quota. No direct tests here; mount integration tests exercise it.
