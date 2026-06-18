# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode_if.h

Read completely: 631 lines.

Generated vnode operation interface header. It is generated from `vnode_if.src` by `vnode_if.sh` and should not be edited directly.

Core contents:
- Declares `vop_default_desc`, one descriptor offset macro per operation, one operation-specific argument structure per VOP, the external descriptor object, and the wrapper prototype.
- `VNODE_OPS_COUNT` is 55.
- Includes non-kernel `<stdbool.h>` compatibility and forward declarations for `struct buf`.

Operation coverage:
- I/O and metadata: `BWRITE`, `OPEN`, `CLOSE`, `READ`, `WRITE`, `FALLOCATE`, `FDISCARD`, `IOCTL`, `FCNTL`, `FSYNC`, `SEEK`, `GETATTR`, `SETATTR`.
- Namespace operations: `PARSEPATH`, `LOOKUP`, `CREATE`, `MKNOD`, `REMOVE`, `LINK`, `RENAME`, `MKDIR`, `RMDIR`, `SYMLINK`, `READDIR`, `READLINK`, `ABORTOP`, `WHITEOUT`.
- Lifecycle and locking: `INACTIVE`, `RECLAIM`, `LOCK`, `UNLOCK`, `ISLOCKED`, `REVOKE`, `PRINT`.
- VM/block integration: `BMAP`, `STRATEGY`, `GETPAGES`, `PUTPAGES`, `MMAP`.
- Policy and event operations: `ACCESS`, `ACCESSX`, `POLL`, `KQFILTER`, `PATHCONF`, `ADVLOCK`.
- ACL and extended attributes: `GETACL`, `SETACL`, `ACLCHECK`, `OPENEXTATTR`, `CLOSEEXTATTR`, `GETEXTATTR`, `LISTEXTATTR`, `DELETEEXTATTR`, `SETEXTATTR`.

Risks and notes:
- This header is part of the generated VOP ABI inside the kernel; descriptor offsets and arg structs must stay synchronized with generated `vnode_if.c` and filesystem operation vectors.
- Several arg structs have version suffixes (`_v2`, `_v3`) reflecting interface evolution while preserving generated names/descriptors.
