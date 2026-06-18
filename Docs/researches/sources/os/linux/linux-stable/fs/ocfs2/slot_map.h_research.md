# File Research: sources/os/linux/linux-stable/fs/ocfs2/slot_map.h

Purpose: declares OCFS2 slot map lifecycle, slot acquisition/release, refresh, lookup, and clear APIs.

Read coverage: complete file read, 28 lines.

Key contents:
- Declares initialization and teardown: `ocfs2_init_slot_info()`, `ocfs2_free_slot_info()`.
- Declares mount/dismount slot operations: `ocfs2_find_slot()`, `ocfs2_put_slot()`.
- Declares refresh and lookup helpers: `ocfs2_refresh_slot_info()`, `ocfs2_node_num_to_slot()`, `ocfs2_slot_to_node_num_locked()`.
- Declares `ocfs2_clear_slot()` for invalidating a specific slot.

Notes:
- `ocfs2_slot_to_node_num_locked()` explicitly requires caller-held `osb_lock`.
- Header name/comment use “slotmap” while the file path is `slot_map.h`; functionality is the slot map interface.
