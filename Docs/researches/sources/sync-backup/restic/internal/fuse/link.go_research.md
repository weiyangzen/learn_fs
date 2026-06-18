## sources/sync-backup/restic/internal/fuse/link.go

Purpose: FUSE node implementation for symlinks restored from snapshot metadata.

Important APIs/types: `link` stores `root`, `forget`, `node`, and `inode`. It implements `fs.NodeForgetter`, `fs.NodeGetxattrer`, `fs.NodeListxattrer`, and `fs.NodeReadlinker`. `newLink` constructs the node. `Readlink` returns `node.LinkTarget`. `Attr` fills inode, mode, UID/GID unless `OwnerIsRoot`, access/change/mod times, link count, symlink target size, and 512-byte block count. `Listxattr` and `Getxattr` delegate to `xattr.go`; `Forget` invokes the cache eviction callback.

Control flow and state: the node is immutable after construction except that `Forget` mutates the owning `treeCache` through the callback. Attribute values are derived from the stored `data.Node`.

Dependencies and integration points: called by directory lookup code for `data.NodeTypeSymlink`. It depends on shared constants such as `blockSize` from file handling and on `nodeToXattrList`/`nodeGetXattr` for xattrs.

Risks and test signals: incorrect link target size or xattr forwarding affects tools inspecting mounted snapshots. `TestLink` validates readlink and xattr behavior; `TestBlocks` validates block count. There is no explicit guard for zero `Links`, unlike regular files, so non-POSIX link metadata should be reviewed if symlink link counts can be zero.
