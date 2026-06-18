# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.h

## Purpose
Internal kernel header for autofs structures, macros, globals, and function prototypes.

## Main Elements
- Defines `VFSTOAUTOFS()` and debug/warning macros.
- Defines lock helper macros for `autofs_mount`.
- `struct autofs_node` stores tree linkage, name, synthetic file number, parent/children, vnode, vnode lock, cache state, wildcard state, callout, retries, and ctime.
- `struct autofs_mount` stores root node, mount pointer, lock, map/from, mountpoint, options, prefix, and last file number.
- `struct autofs_request` stores daemon request identity, copied map/path/key/options fields, timeout task, completion state, wildcard state, and refcount.
- `struct autofs_softc` stores device, cv, global lock, request queue, daemon-open state/session, and request ID counter.
- Declares node, trigger, cache, init/uninit, and vnode helper APIs.
- Declares RB tree prototype for child nodes.

## Dependencies And Integration
Used by autofs core, VFS ops, and vnode ops.

## Risk Notes
This is the contract for autofs lock ordering and lifetime management.
