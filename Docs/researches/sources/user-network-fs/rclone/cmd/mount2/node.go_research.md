# sources/user-network-fs/rclone/cmd/mount2/node.go

Purpose: go-fuse v2 inode/node adapter for rclone VFS files and directories, implementing lookup, directory streams, create/remove/rename, symlinks, attributes, statfs, and open.

Important APIs/types: `Node` embeds `fusefs.Inode` and stores `vfs.Node`; `newNode` caches one FUSE node per VFS node via `Sys`; `dirStream` implements `DirStream` and `FileSeekdirer`.

Control flow: lookups require directory VFS nodes and create child inodes with stable mode attrs. `Readdir` opens the VFS directory, reads all entries, and returns a stream that includes `.` and `..`; `Seekdir(0)` enables repeated directory reads. Namespace mutations call VFS `Mkdir`, `Create`, `Remove`, `Rename`, and symlink APIs, then return go-fuse inodes/attrs. `Open` returns a VFS-backed file handle and direct-I/O flags when needed.

State/persistence: mutates remote namespace/content through VFS. Maintains VFS node-to-FUSE node cache in `Sys`. Dependencies are go-fuse, mountlib, VFS. Risks include stale cached nodes, no inode numbers, unsupported xattrs, directory read all-at-once memory, and rename flag ignorance.
