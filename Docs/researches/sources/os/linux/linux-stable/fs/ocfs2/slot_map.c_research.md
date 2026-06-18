# File Research: sources/os/linux/linux-stable/fs/ocfs2/slot_map.c

Purpose: manages OCFS2 node-to-slot ownership state stored in the slot map system file, supporting mount slot acquisition, release, refresh, and node/slot lookup.

Read coverage: complete file read, 542 lines.

Key structures:
- `struct ocfs2_slot` stores whether a slot is valid and the owning node number.
- `struct ocfs2_slot_info` tracks old vs extended map format, slots per block, slot map inode, mapped buffer heads, total slots, and the in-memory slot array.

Major logic:
- `ocfs2_update_slot_info_old()` reads the legacy `__le16` slot map format.
- `ocfs2_update_slot_info_extended()` reads extended slot entries containing validity and 32-bit node number.
- `ocfs2_refresh_slot_info()` rereads mapped slot map buffers and refreshes in-memory state under `osb_lock`.
- `ocfs2_update_disk_slot()` writes the changed in-memory slot state back to the relevant slot map block.
- `ocfs2_slot_map_physical_size()` verifies the slot map file is large enough for `max_slots` in the selected format.
- `ocfs2_map_slot_buffers()` maps each logical slot-map block through the extent map and reads it into `si_bh`.
- `ocfs2_init_slot_info()` allocates slot info, opens the slot map system inode, maps buffers, and attaches it to `osb`.
- `ocfs2_find_slot()` refreshes slot data, reuses this node’s existing slot if present, otherwise chooses the preferred/free slot, records `osb->slot_num`, and writes it to disk.
- `ocfs2_put_slot()` invalidates this node’s slot on disk and frees slot info during dismount.

Important entry points:
- Lifecycle: `ocfs2_init_slot_info()`, `ocfs2_free_slot_info()`.
- Ownership: `ocfs2_find_slot()`, `ocfs2_put_slot()`, `ocfs2_clear_slot()`.
- Lookup: `ocfs2_node_num_to_slot()`, `ocfs2_slot_to_node_num_locked()`, `ocfs2_refresh_slot_info()`.

Concurrency and dependencies:
- In-memory slot array changes are protected by `osb->osb_lock`.
- Disk writes use `ocfs2_write_block()` against the slot map inode cache.
- Reads validate block numbers and use `OCFS2_BH_IGNORE_CACHE` to force fresh slot-map state.
- Depends on system file lookup, extent maps, heartbeat/node identity context, and OCFS2 buffer I/O.

Risks and edge cases:
- If writing a newly acquired slot fails, the code invalidates the in-memory slot and resets `osb->slot_num` to avoid overwriting a slot another node may own.
- Legacy slot maps cannot represent large node numbers; extended slot map support handles newer layouts.
- Slot map size is checked before mapping; too-small files fail mount setup with `-ENOSPC`.
