# File Research: sources/os/linux/linux-stable/fs/ocfs2/localalloc.c

Purpose: implements OCFS2 node-local allocation windows for data clusters, including default sizing, enable/throttle state, mount/shutdown loading, recovery handoff, reservation/claim/free operations, syncing unused local bits back to the global bitmap, and sliding the local window.

Read coverage: complete file read, 1,318 lines.

Key structures and state:
- `OCFS2_LOCAL_ALLOC(dinode)` accesses the local alloc bitmap payload in a local alloc dinode.
- `osb->local_alloc_bits`, `local_alloc_default_bits`, `local_alloc_state`, `local_alloc_bh`, `osb_la_resmap`, and `la_last_gd` are the main per-node local allocation state.
- Local allocation states include unused, disabled, throttled, and enabled states; this file tests enabled/throttled via `ocfs2_la_state_enabled()`.
- `enum ocfs2_la_event` classifies slide, fragmentation, and ENOSPC events for window resizing.

Major logic:
- `ocfs2_la_default_mb()` picks a default local alloc size based on group descriptor capacity, cluster/block size limits, max default cap, distribution across slots, and local alloc bitmap capacity.
- `ocfs2_la_set_sizes()` applies user-requested or default local alloc sizes, clamping to bitmap capacity.
- `ocfs2_local_alloc_seen_free_bits()` and `ocfs2_la_enable_worker()` re-enable local allocation after enough free space is observed or after throttle timeout.
- `ocfs2_alloc_should_use_local()` checks local alloc state and rejects requests larger than half the current local window.
- `ocfs2_load_local_alloc()` reads the local alloc system inode for the local slot, validates flags and bitmap size, verifies it was recovered cleanly, stores the buffer head in `osb`, and enables local allocation.
- `ocfs2_shutdown_local_alloc()` disables local alloc, locks the global bitmap, journals clearing the local alloc dinode, releases the local alloc buffer, and syncs unused bits back to the main bitmap.
- `ocfs2_begin_local_alloc_recovery()` copies another slot's local alloc dinode, clears it on disk, recomputes ECC, and returns the copy for later cleanup after journal recovery.
- `ocfs2_complete_local_alloc_recovery()` locks the global bitmap and releases unused copied local alloc bits back to the main bitmap in a synchronous transaction.
- `ocfs2_reserve_local_alloc_bits()` locks the local alloc inode, rechecks state under `osb_lock`, slides the window if insufficient free bits exist, and fills an allocation context that owns inode and buffer references.
- `ocfs2_claim_local_alloc_bits()` finds/reserves clear bits, journals the local alloc dinode, marks bits used in the local bitmap, updates reservation map and used count, and returns global cluster offsets.
- `ocfs2_free_local_alloc_bits()` journals the local alloc dinode, clears bits in the local bitmap, and decrements used count for rollback paths.
- `ocfs2_sync_local_to_main()` walks zero bits in a local alloc copy and releases those unused cluster ranges to the global bitmap.
- `ocfs2_recalc_la_window()` shrinks/throttles/disables local alloc after ENOSPC or fragmentation and restores default sizing on normal slides when not throttled.
- `ocfs2_local_alloc_reserve_for_window()` reserves a new contiguous cluster window from the global bitmap, retrying with smaller windows after ENOSPC.
- `ocfs2_local_alloc_new_window()` claims clusters from the global bitmap, initializes local alloc offset/total/used fields, clears the local bitmap, and restarts the reservation map.
- `ocfs2_local_alloc_slide_window()` reserves a new window, clears and syncs the old local alloc copy, installs the new window, and records allocation statistics.

Important entry points:
- Lifecycle: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`, `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation API: `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, `ocfs2_free_local_alloc_bits()`.
- State feedback: `ocfs2_local_alloc_seen_free_bits()`, `ocfs2_la_enable_worker()`.

Concurrency and lifetime:
- Local alloc inode `i_rwsem` serializes window use/slide/disable with local allocation users.
- `osb_lock` protects state and current bit-window sizing.
- Global bitmap inode is locked while syncing old local windows or reserving/claiming new windows.
- Recovery is split: clear the recovered slot's local alloc before dropping journal recovery, then free copied unused bits later when normal cluster locks are safe.
- Allocation contexts returned from reserve hold inode and buffer references and must be freed by the caller.

Important dependencies:
- Uses OCFS2 system-file lookup, inode block reads, journaling, global bitmap/suballocator reservation and release, allocation reservation maps, block ECC, tracepoints, workqueues, and buffer-head I/O.

Risk and edge cases:
- Mount refuses local allocs that contain used bits, totals, or offsets because clean journal replay should have recovered them first.
- Shutdown clears the local alloc before syncing to the main bitmap to avoid double frees after later failures.
- Window throttling can reduce local alloc to disabled state; callers must recheck state after slide attempts.
- Reservation-map mode expects local allocation to go through reservations; the old bitmap scan path asserts reservations are disabled.
- `ocfs2_sync_local_to_main()` only frees zero bits from the local copy; used bits remain allocated to files and must not be released.
