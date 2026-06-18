# File Research: sources/local-fs/ocfs2-tools/libocfs2/slot_map.c

Implements OCFS2 slot-map reading, writing, conversion, and formatting for the userspace library. It supports both legacy 16-bit slot maps and extended slot maps selected by `ocfs2_uses_extended_slot_map()`.

Key responsibilities:
- Byte-swaps legacy and extended slot-map structures on big-endian hosts.
- Reads the `SLOT_MAP_SYSTEM_INODE` through `ocfs2_lookup_system_inode()` and `ocfs2_read_whole_file()`.
- Writes slot maps through cached inode file writes.
- Converts raw on-disk maps into `struct ocfs2_slot_map_data`, a normalized in-memory representation.
- Formats/resizes the slot-map system file to match `s_max_slots`.

Important functions:
- `ocfs2_read_slot_map()` / `ocfs2_read_slot_map_extended()`: public typed wrappers over the common reader.
- `ocfs2_write_slot_map()` / `ocfs2_write_slot_map_extended()`: public typed wrappers over the common writer.
- `ocfs2_load_slot_map()` / `ocfs2_store_slot_map()`: normalized load/store API.
- `ocfs2_format_slot_map()`: validates the system inode, resizes allocation if needed, and writes an empty map.

Dependencies:
- `ocfs2_lookup_system_inode`, `ocfs2_read_whole_file`, `ocfs2_file_write`, cached inode APIs.
- `ocfs2_extend_allocation()` and `ocfs2_truncate()` for slot-map sizing.

Research notes:
- `ocfs2_size_slot_map()` deliberately sets `i_size` to the full allocation, not just bytes needed.
- Legacy maps reject `s_max_slots > OCFS2_MAX_SLOTS`; extended maps allow larger node numbers.
- The writer accepts either full-block byte count or logical map size as a successful write result because `ocfs2_file_write()` may report only `i_size`.
