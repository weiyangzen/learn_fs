# File Research: sources/os/bsd/freebsd-src/sys/fs/fdescfs/fdesc.h

## Purpose
Defines private data structures and flags for FreeBSD `fdescfs`, the synthetic `/dev/fd` filesystem.

## Main Elements
- Mount flags: forced unmount, Linux-style readlink behavior, no-dup behavior, and symlink readlink behavior.
- `struct fdescmount` stores root vnode and mount flags.
- Defines synthetic inode/index constants `FD_ROOT` and `FD_DESC`.
- `fdntype` distinguishes root and descriptor nodes.
- `struct fdescnode` stores hash linkage, vnode backpointer, node type, descriptor number, and synthetic filesystem index.
- Declares global hash mutex, conversion macros, init/uninit hooks, and `fdesc_allocvp()`.

## Dependencies And Integration
Included by fdescfs VFS and vnode operations. The mount flags determine whether fd entries duplicate descriptors or expose link-like targets.

## Risk Notes
Node identity is synthetic and descriptor-number based. Hashing and forced-unmount flag handling must prevent stale vnode reuse during teardown.
