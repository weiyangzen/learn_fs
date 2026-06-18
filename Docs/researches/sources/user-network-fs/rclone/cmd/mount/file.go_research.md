# sources/user-network-fs/rclone/cmd/mount/file.go

Purpose: Linux-only bazil FUSE file node adapter for rclone VFS files.

Important APIs/types: `File` embeds `*vfs.File` with `*FS`; implements `fusefs.Node`, `NodeSetattrer`, `NodeOpener`, `NodeFsyncer`, xattr interfaces returning `ENOSYS`, and `NodeReadlinker`.

Control flow: `Attr` fills uid/gid, mode, size, block count, and times from VFS. `Setattr` supports mtime and truncate unless VFS disables modtime. `Open` passes FUSE flags through to VFS, returns a `FileHandle`, and requests direct I/O when size is unknown or configured. `Readlink` delegates to VFS symlink support.

State/persistence: remote/VFS mutation occurs on truncate and modtime changes; open handles may later mutate via writes. No local persistence. Dependencies are bazil fuse, VFS, and package error translation. Risks include direct-IO performance tradeoffs, mode masking of append-only, xattr unsupported behavior, and backend support for truncate/modtime/symlink.
