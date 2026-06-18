# File Research: sources/os/linux/linux/fs/ocfs2/reservations.c

`reservations.c` implements OCFS2 allocation reservation windows. Reservations track free bitmap regions per allocation context to improve locality and reduce fragmentation for local allocation and directory growth.

Main responsibilities:
- Maintains reservations in an rbtree ordered by window start, with an LRU list for fallback stealing.
- Uses a single static `resv_lock` spinlock to serialize all reservation map updates.
- Computes reservation window sizes from mount tunables:
  - regular reservations use `osb_resv_level`.
  - directory reservations use `osb_dir_resv_level`.
  - `ocfs2_dir_resv_allowed()` reports whether directory reservations are enabled.
- Initializes and tears down state:
  - `ocfs2_resv_init_once()` initializes a reservation object.
  - `ocfs2_resv_set_type()` marks temporary or directory reservations.
  - `ocfs2_resmap_init()` initializes a reservation map.
  - `ocfs2_resmap_restart()` clears existing reservations and binds the map to a new disk bitmap and length.
  - `ocfs2_resmap_uninit()` is currently a symmetry no-op.
- Discards reservations:
  - `ocfs2_resv_discard()` clears length/start/last-allocation tracking and removes the reservation from the rbtree and LRU.
  - `ocfs2_resmap_clear_all_resv()` discards every reservation during restart.
- Inserts reservations with overlap checks in `ocfs2_resv_insert()`.
- Finds free reservation windows:
  - `ocfs2_find_resv_lhs()` locates the reservation containing or immediately before a goal.
  - `ocfs2_resmap_find_free_bits()` scans a bitmap gap for the best contiguous free run up to the wanted length.
  - `__ocfs2_resv_find_window()` searches gaps around existing reservations.
  - `ocfs2_resv_find_window()` retries from the previous allocation goal and then from the beginning.
  - `ocfs2_cannibalize_resv()` steals all or part of the oldest LRU reservation when no fresh gap can satisfy the request.
- Exposes allocation-facing APIs:
  - `ocfs2_resmap_resv_bits()` returns a valid reservation window, creating one if the reservation is empty.
  - `ocfs2_resmap_claimed_bits()` records that a caller consumed bits from the front of the reservation and adjusts or discards the window.

Debug behavior:
- Under debugfs builds, `OCFS2_CHECK_RESERVATIONS` validates that rbtree windows are ordered, non-empty, inside bitmap bounds, non-overlapping, and cover only free disk bitmap bits.
- On validation failure, it dumps both rbtree and LRU state before `BUG()`.

Key invariants:
- Reservation windows never overlap.
- A claimed allocation must start at the reservation start.
- Temporary reservations avoid over-allocation by limiting wanted size to the current request.
- Reservation maps can be disabled globally by reservation level zero, in which case callers receive `-ENOSPC` and fall back to normal allocation.
