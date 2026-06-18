# File Research: sources/os/linux/linux-stable/fs/ocfs2/reservations.h

Purpose: declares OCFS2 allocation reservation structures, flags, tuning bounds, and reservation-map APIs.

Read coverage: complete file read, 144 lines.

Key contents:
- Defines reservation level bounds: `OCFS2_DEFAULT_RESV_LEVEL`, `OCFS2_MAX_RESV_LEVEL`, and `OCFS2_MIN_RESV_LEVEL`.
- Defines `struct ocfs2_alloc_reservation` with rb-tree node, current window start/length, last allocation start/length, LRU list node, and flags.
- Defines flags for in-use windows, temporary windows, and directory reservations.
- Defines `struct ocfs2_reservation_map` with rb-tree root, disk bitmap pointer, owning superblock, bitmap length, and LRU list.
- Declares initialization, type setting, discard, restart, uninit, reserve-bits, and claimed-bits APIs.

Important behavior:
- The header documents that `ocfs2_resmap_restart()` discards existing reservations when a new bitmap is supplied.
- `ocfs2_resmap_resv_bits()` returns the currently valid reserved allocation range and may allocate a window if the reservation is empty.
- `ocfs2_resmap_claimed_bits()` must be called when allocation bits are consumed so reservation state can be trimmed consistently.

Risks:
- Reservation objects are caller-owned, while the map stores their rb/list links; callers must discard or consume windows before object lifetime ends.
- `cstart` passed to `ocfs2_resmap_claimed_bits()` is expected to match the reservation start returned earlier.
