# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.h

## Summary
Kernel-private AUTOFS header defining nodes, mounts, request structures, global state, tunables, debug macros, and internal APIs.

## Main Responsibilities
- Define `AUTOFS_ROOTINO`, `VFSTOAUTOFS()`, and `VTOI()`.
- Declare vnode operation descriptors, pools, global softc, workqueue, and tunables.
- Define `struct autofs_node` with RB-tree child relationships, vnode pointer, cache state, wildcard state, callout, retry count, and creation time.
- Define `struct autofs_mount` with root node, mount pointer, lock, map metadata, and inode counter.
- Define `struct autofs_request` for daemon-triggered mount requests.
- Define `struct autofs_softc` for the global request queue and control-device state.
- Declare trigger, cache, flush, node, and timeout functions.

## Risks
Node names are ordered by `strcmp()` in an RB tree. Many routines require the owning mount lock or global softc lock; misuse can corrupt tree/request state.
