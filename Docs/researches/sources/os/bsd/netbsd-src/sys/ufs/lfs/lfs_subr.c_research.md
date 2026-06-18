# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_subr.c

## Scope

Provides shared LFS kernel support for reserved memory, segment/prelocks, cleaner locks, directory-operation draining, writer exclusion, cleaner wakeups, and cleaning-list bookkeeping.

## APIs And Behavior

- `lfs_setup_resblks()` and `lfs_free_resblks()` allocate/free per-mount emergency buffers and pools used while holding the segment lock or under memory pressure.
- `lfs_malloc()` first tries nonblocking allocation, then falls back to typed reserved buffers tracked in a hash; `lfs_free()` returns reserved buffers or frees normal allocations.
- `lfs_seglock()`/`lfs_segunlock()` serialize segment writing, set up `struct segment`, maintain I/O counts, handle sync/checkpoint waits, write superblocks, run automatic segment cleaning promotion, and clear completed dirops.
- `lfs_prelock()`/`lfs_preunlock()` provide the underlying recursive per-LWP prerequisite lock; pagedaemon callers can fail rather than sleep.
- `lfs_writer_enter()`, `lfs_writer_tryenter()`, and `lfs_writer_leave()` exclude new directory operations while a writer drains metadata.
- `lfs_cleanerlock()`/`lfs_cleanerunlock()` serialize cleaner activity and clear per-cleaning vnode references.
- `lfs_segunlock_relock()` temporarily drops nested segment locks, wakes the cleaner for free segments, waits for space, then restores the previous lock depth.
- `lfs_setclean()`, `lfs_clrclean()`, and `lfs_seguse_clrflag_all()` manage cleaner vnode lists and segment-use flag maintenance.

## State And Dependencies

This file centralizes shared state protected by `lfs_lock`: reserved-buffer ownership, `lfs_prelock`, `lfs_seglock`, `lfs_iocount`, cleaner and writer flags, `lfs_dchainhd`, `lfs_cleanhd`, and condition variables. It depends on LFS superblock/segment accessors, segment writer functions, Ifile cleaner info, vnode references, and NetBSD pool/malloc primitives.

## Risks And Invariants

Segment lock nesting is intentional and tied to a single prelock owner. Reserved blocks must not be freed while still marked in use. Checkpoint unlock has subtle ordering: I/O completion, superblock writes, active-superblock switching, and dirop unmarking must remain coordinated. Directory-operation references are cleared through marker inodes to tolerate list mutation while dropping `lfs_lock`.
