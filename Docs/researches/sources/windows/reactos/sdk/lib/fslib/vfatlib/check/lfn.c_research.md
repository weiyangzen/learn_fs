# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/lfn.c

Implements VFAT long-filename parsing, validation, repair prompts, checksum repair, and orphan cleanup.

Key elements:
- Defines packed `LFN_ENT`, matching the 32-byte VFAT long-name directory slot format.
- Parser state is module-global: collected Unicode name buffer, checksum, expected slot, slot offsets, and part count.
- `cnv_unicode` converts UTF-16LE name data to multibyte output, escaping unconvertible characters with FAT-style escape notation.
- `lfn_add_slot` consumes LFN directory entries, validates sequence numbers, checksum, reserved field, and start cluster.
- `lfn_get` attaches collected LFN slots to the following short directory entry after checksum validation.
- `lfn_fix_checksum` updates alias checksums across an LFN slot range.
- `lfn_check_orphaned` deletes or leaves unattached LFN fragments depending on mode.

Dependencies:
- Uses `fs_write` for in-place repairs.
- Uses `file_name` to display short aliases.
- Uses checker globals/macros: `interactive`, `rw`, `mem_queue`, `get_key`, `qalloc`, `alloc`, `free`.

Research notes:
- Noninteractive behavior is conservative for many structural LFN problems, but auto-fixes reserved/start fields; ReactOS only auto-deletes orphaned LFN slots when read-write is enabled.
- The parser is stateful and assumes directory traversal calls `lfn_add_slot` for consecutive LFN entries and `lfn_get` on the following non-LFN entry.
