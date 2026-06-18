# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/dispatcher.c

This is the central PUFFS request dispatcher. It takes kernel request frames, decodes `preq_opclass` and `preq_optype`, invokes the corresponding filesystem operation callback in `struct puffs_ops`, fills reply fields, records errors in `preq_rv`, and sends replies back when required.

`puffs__ml_dispatch` dispatches within the main-loop context, then either enqueues the reply frame to the kernel fd or destroys no-reply frames. `puffs_dispatch_create` and `puffs_dispatch_exec` expose semi-supported manual dispatch through call contexts.

The main `dispatch` function handles VFS operations such as unmount, statvfs, sync, filehandle-to-node, node-to-filehandle, and extattr control. It handles many vnode operations: lookup, create, mknod, open/close, access, getattr/setattr with optional filesystem TTL support, mmap, fsync, seek, remove, link, rename, mkdir/rmdir, symlink, readdir, readlink, reclaim, inactive, pathconf, advisory locking, print, abortop, read/write, poll, extended attributes, fallocate, and fdiscard. It also handles PUFFS error notifications.

It integrates path building and pnode cookies when enabled, updates lookup counts, adjusts path objects on create/lookup/rename, reserves max message space for variable-size read/readdir/vptofh responses, and supports operation dump hooks plus pre/post operation callbacks.

Risks are broad dispatch complexity, optional callback defaults that sometimes return success and sometimes `EOPNOTSUPP`/`EIO`, path and lookup-count consistency, variable reply buffer sizing, and old comments noting return-value and kernel synchronization audit needs.
