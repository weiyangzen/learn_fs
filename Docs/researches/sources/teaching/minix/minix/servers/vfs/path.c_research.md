# File Research: sources/teaching/minix/minix/servers/vfs/path.c

Central pathname resolution implementation. It mediates between VFS vnode/vmnt state and file-server `REQ_LOOKUP` semantics.

Key behavior:
- `advance` resolves a path from a starting vnode, allocates a temporary vnode, calls internal `lookup`, reuses an existing vnode if present, fills new vnode metadata otherwise, increments vnode references, and downgrades locks when requested.
- `eat_path` chooses root or working directory based on absolute vs relative path and calls `advance`.
- `last_dir` resolves all but the final component, returns the parent directory vnode, and rewrites `resolve->l_path` to the final component. It handles trailing slashes, symlinks in the final component, relative symlink targets, absolute symlink restarts, and mountpoint crossings.
- Internal `lookup` sends `REQ_LOOKUP` to filesystem servers, tracks `EENTERMOUNT`, `ELEAVEMOUNT`, and `ESYMLINK`, rewrites the remaining path buffer based on `char_processed`, locks the current `vmnt`, and follows mount tree transitions.
- `lookup_init` initializes the mutable `struct lookup` contract used across VFS.
- `get_name` scans a directory with `req_getdents` to find the name corresponding to a child inode.
- `canonical_path` resolves symlinks, climbs parent directories with `..`, crosses mount roots back to mounted-on vnodes, and builds an absolute path.
- `do_socketpath` lets the UDS service check or create on-disk socket path nodes on behalf of a blocked user process.

Important dependencies:
- `request.c` for `req_lookup`, `req_rdlink`, `req_getdents`, `req_mknod`.
- `vnode.c` and `vmnt.c` for locks, references, and mount lookup.
- `protect.c` for socket path permission checks.

Notable implementation details:
- Path resolution mutates the caller-provided path buffer throughout lookup.
- VMNT read requests are initially taken as write locks and later downgraded, mirroring vnode OPCL/read downgrade behavior.
- Symlink depth is bounded by `_POSIX_SYMLOOP_MAX`.
- `DO_POSIX_PATHNAME_RES` is disabled, so trailing slashes are stripped in the historical Unix style.
