# File Research: sources/os/linux/linux/fs/ocfs2/localalloc.c

`localalloc.c` implements OCFS2’s per-node local allocation window. It lets a mounted node reserve a contiguous slice of the global bitmap and satisfy smaller cluster allocations locally, reducing global bitmap contention.

Main responsibilities:
- Computes default local allocation size in `ocfs2_la_default_mb()`, balancing group descriptor capacity, cluster size, block size, max slots, and a 256 MiB default cap.
- Applies requested/default sizes with `ocfs2_la_set_sizes()`.
- Tracks enabled/throttled/disabled local alloc state. `ocfs2_local_alloc_seen_free_bits()` and delayed `ocfs2_la_enable_worker()` can re-enable allocation after free-space conditions improve.
- Decides whether an allocation should use local alloc in `ocfs2_alloc_should_use_local()`, based on state and request size.
- Loads the local alloc system inode for the current slot with `ocfs2_load_local_alloc()`, validates flags and bitmap size, and requires the on-disk local alloc to be clean/recovered before enabling it.
- Shuts down local alloc with `ocfs2_shutdown_local_alloc()`, disabling the state, clearing the local alloc dinode, and returning unused local-window bits to the global bitmap in one window-move transaction.
- Supports recovery:
  - `ocfs2_begin_local_alloc_recovery()` copies and clears a dead slot’s local alloc before releasing the recovered journal.
  - `ocfs2_complete_local_alloc_recovery()` later returns unused bits to the global bitmap under normal cluster locking and synchronous transaction handling.
- Reserves local alloc bits in `ocfs2_reserve_local_alloc_bits()`, double-checking state under inode mutex and sliding the window if insufficient free bits remain.
- Claims and frees local bits in `ocfs2_claim_local_alloc_bits()` and `ocfs2_free_local_alloc_bits()`, journaling the local alloc dinode and updating reservation maps.
- Counts used bits with `memweight()`, finds clear extents through the reservation map when enabled, and falls back to bitmap scanning when reservations are disabled.
- Clears local alloc state with `ocfs2_clear_local_alloc()`.
- Syncs unused local allocation bits back to the main bitmap in `ocfs2_sync_local_to_main()` by finding zero-bit runs and releasing corresponding global clusters.
- Recalculates local alloc window size after slide, fragmentation, or ENOSPC events. Fragmentation/ENOSPC halves the window, throttles or disables local alloc, and schedules a delayed re-enable.
- Reserves a new global bitmap window, creates a new local alloc window, and slides from the old window to the new one through `ocfs2_local_alloc_slide_window()`.

Key invariants:
- The local alloc inode mutex serializes window changes and state checks.
- Before a window move, the local alloc dinode is cleared first to avoid double-freeing bits if later steps fail.
- Recovery clears a dead node’s local alloc before considering its journal fully released, but returns the bits later outside the sensitive recovery context.
- Local alloc never serves allocations larger than half the window.
