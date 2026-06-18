# File Research: sources/teaching/minix/minix/servers/vfs/request.h

Defines response structures shared by request wrappers and callers.

Key structures:
- `node_details_t`: filesystem endpoint, inode number, mode, size, uid, gid, and special-file device number.
- `lookup_res_t`: same core vnode metadata plus `char_processed` and `symloop` fields used by path lookup to continue after mount transitions or symlink expansion.

Usage:
- `node_details_t` is filled by creation, new-node, and read-super requests, then copied into VFS vnode state.
- `lookup_res_t` is filled by `req_lookup` and consumed by `path.c` for multi-filesystem pathname traversal.
