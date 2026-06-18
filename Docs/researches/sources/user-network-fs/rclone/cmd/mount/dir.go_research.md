# sources/user-network-fs/rclone/cmd/mount/dir.go

Purpose: Linux-only bazil FUSE directory node adapter for rclone VFS directories. It implements directory attributes, lookup, listing, create, mkdir, remove, rename, fsync, links, and symlinks.

Important APIs/types: `Dir` embeds `*vfs.Dir` with `*FS`; implements bazil `fusefs.Node`, `NodeSetattrer`, `NodeRequestLookuper`, `HandleReadDirAller`, `NodeCreater`, `NodeMkdirer`, `NodeRemover`, `NodeRenamer`, `NodeFsyncer`, `NodeLinker`, `NodeSymlinker`, and `NodeMknoder`.

Control flow: lookups call `vfs.Dir.Stat`, reuse cached FUSE nodes via `vfs.Node.Sys`, and set entry cache timeout. `ReadDirAll` maps VFS entries to FUSE dirents, skips names over `mountlib.MaxLeafSize`, and marks symlinks. Create/mkdir wrap VFS creation and cache new nodes. Rename delegates to VFS and invalidates the destination entry asynchronously to avoid deadlocks. Symlink creates a VFS symlink and wraps it as a file node; `Mknod` rejects device nodes but creates/closes a regular file for NFS clients that prefer mknod.

State/persistence: mutates remote/VFS namespace for create, mkdir, remove, rename, symlink, modtime, and sync. Dependencies are bazil fuse, mountlib, VFS, and error translation in `fs.go`. Risks include node-cache consistency, async invalidation races, unsupported hard links, and long-name skipping.
