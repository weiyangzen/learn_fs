# File Research: sources/os/linux/linux/fs/ocfs2/reservations.h

`reservations.h` declares the data structures and APIs for OCFS2 allocation reservation windows.

Main contents:
- Defines reservation level bounds:
  - default `OCFS2_DEFAULT_RESV_LEVEL`
  - max `OCFS2_MAX_RESV_LEVEL`
  - min `OCFS2_MIN_RESV_LEVEL`
- Defines `struct ocfs2_alloc_reservation`:
  - rbtree node for ordered reservation map membership.
  - current window start and length.
  - last allocation start and length used as the next search goal.
  - LRU list node.
  - flags.
- Defines reservation flags:
  - `OCFS2_RESV_FLAG_INUSE`: reservation is linked into the rbtree.
  - `OCFS2_RESV_FLAG_TMP`: temporary reservation discarded after use.
  - `OCFS2_RESV_FLAG_DIR`: directory-specific reservation sizing.
- Defines `struct ocfs2_reservation_map`:
  - rbtree of reservations.
  - disk bitmap pointer used to verify free bits.
  - owning `ocfs2_super`.
  - bitmap length.
  - LRU list of reservation objects.
- Declares setup and type APIs:
  - `ocfs2_resv_init_once()`
  - `ocfs2_resv_set_type()`
  - `ocfs2_dir_resv_allowed()`
- Declares map lifecycle APIs:
  - `ocfs2_resmap_init()`
  - `ocfs2_resmap_restart()`
  - `ocfs2_resmap_uninit()`
- Declares allocation-facing APIs:
  - `ocfs2_resmap_resv_bits()` to obtain still-valid reservation bits or create a new window.
  - `ocfs2_resmap_claimed_bits()` to notify the reservation map that clusters were used.
  - `ocfs2_resv_discard()` to truncate and unlink a reservation.

Key invariants:
- `ocfs2_resmap_claimed_bits()` must be called whenever reserved bits are consumed so the map remains accurate.
- `ocfs2_resmap_restart()` invalidates existing reservations when the backing bitmap changes, such as during local allocation window slides.
