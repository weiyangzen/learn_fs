# File Research: sources/os/linux/linux/fs/ocfs2/slot_map.h

`slot_map.h` declares the OCFS2 slot-map API used by mount, dismount, recovery, and per-slot resource code.

Main contents:
- Declares initialization and cleanup:
  - `ocfs2_init_slot_info()`
  - `ocfs2_free_slot_info()`
- Declares mount/dismount slot lifecycle:
  - `ocfs2_find_slot()` to acquire a slot for the local node.
  - `ocfs2_put_slot()` to release the local node’s slot and free slot information.
- Declares refresh and lookup helpers:
  - `ocfs2_refresh_slot_info()`
  - `ocfs2_node_num_to_slot()`
  - `ocfs2_slot_to_node_num_locked()`
- Declares `ocfs2_clear_slot()` for explicit slot invalidation.

Key invariants:
- `ocfs2_slot_to_node_num_locked()` requires caller-side locking, as indicated by its name and implementation.
- Format-specific slot-map details are private to `slot_map.c`.
