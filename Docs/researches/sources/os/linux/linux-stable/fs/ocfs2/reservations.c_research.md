# File Research: sources/os/linux/linux-stable/fs/ocfs2/reservations.c

Purpose: implements in-memory allocation reservation windows for OCFS2 bitmap allocation, improving locality by reserving free ranges per allocation context.

Read coverage: complete file read, 824 lines.

Key responsibilities:
- Maintains non-overlapping reservation windows in an rb-tree and an LRU list.
- Sizes reservation windows from mount reservation levels, with separate sizing for directory reservations.
- Validates reservation invariants under debug builds.
- Finds free bitmap gaps not covered by existing reservations.
- Discards, restarts, and updates reservations as allocation windows are consumed.

Major logic:
- `ocfs2_resmap_init()` initializes an empty reservation map tied to an `ocfs2_super`.
- `ocfs2_resmap_restart()` clears all current windows and attaches a new disk bitmap/length, typically when the local allocation window changes.
- `ocfs2_resv_insert()` inserts a non-overlapping reservation into the rb-tree and appends it to the LRU.
- `ocfs2_find_resv_lhs()` finds the reservation containing or immediately before a goal bit.
- `ocfs2_resmap_find_free_bits()` scans a bitmap gap for the best free run up to the wanted length.
- `ocfs2_resv_find_window()` tries to place a reservation near the last allocation, retries from zero, and finally cannibalizes the oldest reservation if no gap is available.
- `ocfs2_resmap_resv_bits()` returns a valid reserved range to the allocator, allocating a new window if needed.
- `ocfs2_resmap_claimed_bits()` trims or removes a reservation after bits are allocated and records the most recent allocation for future placement.

Concurrency and dependencies:
- All reservation tree/list mutations are serialized by the file-global `resv_lock`.
- The map points directly at an externally supplied disk bitmap; reservations are invalidated on restart rather than persisted.
- Uses OCFS2 bitmap helpers, rb-tree APIs, list APIs, tracepoints, and optional debug validation.

Risks and edge cases:
- Reservation windows must never overlap each other or allocated disk bitmap bits; debug mode checks and dumps state before BUG.
- Temporary reservations avoid over-allocation by requesting only the caller’s needed length.
- Cannibalization can shrink or remove older reservations to make progress when free gaps are not available.
- `ocfs2_resmap_resv_bits()` returns `-ENOSPC` when reservations are disabled, so callers must fall back to non-reserved allocation.
