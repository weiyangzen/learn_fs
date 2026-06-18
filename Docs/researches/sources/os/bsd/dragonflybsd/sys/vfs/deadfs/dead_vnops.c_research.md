# File Research: sources/os/bsd/dragonflybsd/sys/vfs/deadfs/dead_vnops.c

Read completely: 211 lines.

## Role

This file defines DragonFlyBSD's dead vnode operation table. Dead vnodes are vnodes whose backing filesystem object has been revoked, reclaimed, forcibly unmounted, or otherwise made unusable. The operations mostly fail predictably while allowing cleanup paths such as close and inactive/reclaim to complete safely.

## Main Responsibilities

- Define `dead_vnode_vops` and export `dead_vnode_vops_p`.
- Return stable errors for operations on dead vnodes:
  - Access, getattr, setattr, readdir, readlink, pathconf, and advisory locking use `vop_ebadf`.
  - Lookup returns `ENOTDIR`.
  - Open returns `ENXIO`.
  - Read returns EOF for tty vnodes and `EIO` otherwise.
  - Write and bmap return `EIO`.
  - Ioctl returns `ENOTTY`.
- Allow safe cleanup:
  - `dead_close()` succeeds and carefully decrements `v_opencount` and `v_writecount` if they are positive.
  - Inactive and reclaim are no-ops.
- Panic on operations that should never be issued to dead vnodes via `dead_badop()`.
- Provide `dead_print()` diagnostics.

## Synchronization and Lifetime Model

- `dead_close()` upgrades/retries the vnode lock before touching open/write counts.
- The close path deliberately avoids warning or panicking on surprising open-count state because forced unmount or revoke can close the backing object underneath a descriptor.
- `VNODEOP_SET(dead_vnode_vops)` registers the table with the vnode operation framework.

## Important Interactions

- Used by generic vnode reclamation/revocation paths to replace filesystem-specific operations after a vnode is no longer backed by a valid object.
- TTY read behavior supports legacy semantics where reads from a revoked tty can return EOF rather than a hard I/O error.

## Research Notes

- This is defensive infrastructure: its correctness is mostly about returning stable errors and avoiding panics during teardown.
- The only operation with meaningful state mutation is `dead_close()`.
- `dead_badop()` marks old create/link/mkdir/mknod/remove/rename/rmdir/symlink operations as impossible on dead vnodes.
