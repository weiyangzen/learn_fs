# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.h

## Summary
Shared autofs kernel structures, macros, globals, and internal function declarations.

## Main Responsibilities
- Defines root inode and conversion macros for mount and vnode private data.
- Declares autofs caches, softc, dev ops, vnode ops, and debug variable.
- Defines debug/warning print macros.
- Defines `struct autofs_node` for tree nodes, vnode association, cache/wildcard state, callout, retry count, and ctime.
- Defines `struct autofs_mount` for root node, lock, map/mount/options/prefix strings, and inode allocator.
- Defines `struct autofs_request` for daemon queue entries and timeout task.
- Defines `struct autofs_softc` for device, condition variable, lock, request queue, opener state, daemon process group, and request ID allocator.
- Declares trigger/cache/path/flush/node/vnode helpers and RB prototypes.

## Important Behavior
Autofs nodes are organized as RB trees under each parent and are separate from vnode lifetime; `autofs_reclaim()` clears the vnode pointer but nodes are freed by explicit node deletion.

## Risks
The structures mix mount-level locks, node-level vnode locks, condition variables, callouts, and reference-counted request objects. Lock ordering must remain consistent between VOP paths, triggers, and unmount.
