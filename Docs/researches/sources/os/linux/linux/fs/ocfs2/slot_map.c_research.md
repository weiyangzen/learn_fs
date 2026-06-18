# File Research: sources/os/linux/linux/fs/ocfs2/slot_map.c

`slot_map.c` implements OCFS2 slot-map management. Slots associate mounted cluster nodes with per-slot resources such as journals and local quota/local allocation files.

Main responsibilities:
- Defines in-memory slot state:
  - `struct ocfs2_slot` records whether a slot is valid and which node number owns it.
  - `struct ocfs2_slot_info` stores slot-map format, backing inode, mapped buffer heads, slot count, and in-memory slot array.
- Supports old and extended on-disk formats:
  - old format stores `__le16` node numbers, using `OCFS2_INVALID_SLOT` for empty slots.
  - extended format stores explicit valid bits and 32-bit node numbers.
- Refreshes slot state:
  - `ocfs2_refresh_slot_info()` rereads all mapped slot-map blocks, validates them, and updates the in-memory slot array under `osb_lock`.
  - `ocfs2_update_slot_info_old()` and `ocfs2_update_slot_info_extended()` decode on-disk formats.
- Writes slot changes:
  - `ocfs2_update_disk_slot_old()` rewrites all old-format slots into the first block.
  - `ocfs2_update_disk_slot_extended()` updates the one extended-format entry containing the requested slot.
  - `ocfs2_update_disk_slot()` serializes the in-memory to disk copy under `osb_lock`, then writes the affected block.
- Initializes mapped slot buffers:
  - `ocfs2_slot_map_physical_size()` ensures the slot-map file is large enough for `max_slots`.
  - `ocfs2_map_slot_buffers()` maps logical slot-map blocks to physical blocks and reads them uncached.
  - `ocfs2_init_slot_info()` allocates flexible slot info, gets the slot-map system inode, maps buffers, and installs it in `osb`.
- Exposes lookup and slot lifecycle:
  - `ocfs2_node_num_to_slot()` maps a node number to its slot.
  - `ocfs2_slot_to_node_num_locked()` maps a slot to node number while caller holds `osb_lock`.
  - `ocfs2_find_slot()` refreshes slot info, reuses this node’s existing slot if present, otherwise chooses the preferred or first empty slot, writes it to disk, and sets `osb->slot_num`.
  - `ocfs2_clear_slot()` invalidates a specified slot and writes it.
  - `ocfs2_put_slot()` clears the mounted node’s slot, writes it, and frees slot info.
  - `ocfs2_free_slot_info()` releases buffers and the slot-map inode.

Key invariants:
- In-memory slot array mutation is protected by `osb_lock`.
- Slot-map file size is validated before mapping buffer heads.
- A failed disk write during slot acquisition invalidates the local in-memory slot to avoid later dismount overwriting a slot another node may have acquired.
- `ocfs2_put_slot()` frees the whole slot-info structure after clearing the local node’s slot.
