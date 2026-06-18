# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/subr.c

## Purpose
Utility implementation for perfuse node lifecycle, file-handle management, nodeid cache, and xattr namespace translation.

## Main Responsibilities
- Allocates and initializes PUFFS nodes plus `perfuse_node_data`.
- Destroys nodes, freeing readdir buffers and private data.
- Creates, destroys, and resolves read/write FUSE file handles on nodes.
- Provides a simple node path/name helper.
- Maps NetBSD extattr namespaces to Linux/FUSE xattr prefixes and filters listed xattrs.
- Maintains a hash table from FUSE nodeid to `perfuse_node_data`.

## Key Implementation Notes
- New nodes default file handles to `FUSE_UNKNOWN_FH` and parent nodeid to the parent’s FUSE nodeid or root.
- `perfuse_get_fh()` can use a write handle for reads when no read handle exists.
- `perfuse_node_cache()` inserts node data into the nodeid hash; `perfuse_cache_flush()` removes it.
- Xattr translation preserves matching reserved prefixes, prepends `user.` for user access to reserved-looking names, and prepends `system.` for system namespace names without a reserved prefix.

## Dependencies
- PUFFS node allocation APIs.
- `sys/hash.h` for nodeid hashing.
- `perfuse_priv.h`.
