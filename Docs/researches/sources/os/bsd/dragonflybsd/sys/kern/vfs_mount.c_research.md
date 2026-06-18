# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_mount.c

## Summary
Implements mount structure initialization, mount-list management, mount busy interlocks, vnode-to-mount association, mount vnode scans, vnode flushing, background vnode reclamation, and BIO sync hooks.

## Main Responsibilities
- Initializes mount globals and dummy mount in `vfs_mount_init()`.
- Allocates normal and special vnodes with `getnewvnode()` / `getspecialvnode()`.
- Implements `vfs_busy()` / `vfs_unbusy()` unmount interlocks.
- Allocates root mounts and initializes generic mount structures.
- Maintains mount list and RB lookup by fsid.
- Runs `vnlru` kernel thread to free vnode pressure.
- Scans mount vnode lists with `vmntvnodescan()`.
- Flushes vnodes during unmount with `vflush()`.
- Registers and invokes `bio_ops` sync callbacks.

## Important Behavior
Mount list scans are removal-safe via active scan descriptors. Each scanned mount can be held and optionally busied before callback execution. `vmntvnodescan()` similarly tracks active vnode scans so vnode removal can advance scan cursors safely.

`vflush()` scans all vnodes on a mount with VX locks, finalizes candidates, forcibly detaches when requested, and reports `EBUSY` for still-referenced vnodes unless force-close rules apply. Device vnodes are protected from force-close.

The `vnlru` thread periodically synchronizes vnode counts, frees excess cached/inactive vnodes, and runs namecache hysteresis cleanup.

## Risks
`mountlist_exists()` is documented as a best-effort pointer validity check for quota/PFS use and explicitly does not guarantee the same mount pointer will be used later. Many functions rely on mount tokens and vnode scan interlocks; misuse by callbacks can break assumptions.
