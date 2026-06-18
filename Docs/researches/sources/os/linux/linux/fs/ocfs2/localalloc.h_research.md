# File Research: sources/os/linux/linux/fs/ocfs2/localalloc.h

`localalloc.h` declares the internal API for OCFS2 per-node local allocation windows.

It exposes:
- Load/shutdown: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`.
- Sizing: `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation policy: `ocfs2_alloc_should_use_local()`.
- Reservation/claim/free operations for local bits.
- Free-space notification and delayed re-enable worker.

The header is consumed by allocation, journal recovery, and mount/shutdown paths that need to use or clean up slot-local allocation state.
