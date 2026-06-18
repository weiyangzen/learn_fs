# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.h

## Purpose

Defines the public pseudofs API, callback types, node/instance structures, flags, limits, and the `PSEUDOFS()` registration macro used by procfs-like synthetic filesystems.

## Main Interface

Types:
- `pfs_type_t`: root, directory, `.`/`..`, file, symlink, and process-directory node kinds.
- `struct pfs_info`: filesystem instance name, init/uninit callbacks, root node, mutex, and file-number allocator.
- `struct pfs_node`: immutable node identity/callback fields plus mutex-protected data, file number, parent/children/sibling pointers, and name.

Flags:
- `PFS_RD`, `PFS_WR`, `PFS_RDWR`: readable/writeable file semantics.
- `PFS_RAWRD`, `PFS_RAWWR`, `PFS_RAW`: raw `uio` handlers instead of sbuf text buffering.
- `PFS_PROCDEP`: process-dependent nodes.
- `PFS_NOWAIT`: nonblocking allocation option.
- `PFS_AUTODRAIN`: streaming sbuf reads.

Callback contracts:
- fill callbacks are called with proc held but unlocked.
- attr, visibility, ioctl, getextattr, and close callbacks document process-lock expectations through their macros/comments.

Public functions include mount/root/statfs/init/uninit, node creation, lookup, purge, and destroy.

`PSEUDOFS(name, version, flags)` creates per-filesystem `pfs_info`, mount/init/uninit wrappers, VFS ops, `VFS_SET`, module version, and pseudofs module dependency.

## Integration Points

Used by `procfs` and other synthetic filesystems to define hierarchy and behavior without writing their own VFS/vnode core.

## Risks and Review Notes

The callback locking contract is central: callers and implementers must agree on whether `struct proc` is locked, held, or unlocked. `struct pfs_node` comments define lock ownership for fields and require parent-before-child locking to avoid deadlocks.
