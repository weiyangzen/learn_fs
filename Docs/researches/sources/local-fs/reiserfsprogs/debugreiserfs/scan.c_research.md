# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/scan.c

Implements scanning by filename pattern, key, name lookup, item-map saving, and map printing.

Primary flows:
- `DO_SCAN_FOR_NAME`: regex-scan selected blocks for directory entries matching a name pattern, index names by name and pointed key, then scan for matching file items.
- `DO_SCAN`: prompt for dirid/objectid and scan selected blocks for matching items or directory entries.
- `DO_LOOK_FOR_NAME`: interactively search a directory using tree lookup, locate the file, and flush a map.
- `DO_FILE_MAP`: print previously saved item records.

Data structures:
- `saved_name`: stores found names, parent directory key, pointed object key, occurrence count, item tree, and duplicate-name chain.
- `saved_item`: records item header, block number, item index, and entry position.
- `file_map`: experimental in-memory layout with indirect block head and direct-item tails.

Storage/indexing:
- Uses GNU obstacks for name/item allocation.
- Uses `tsearch`/`tfind` trees for name, key, and item indexing.
- Writes one map file per matched name as `<map_file>.<n>` when `-a` is supplied.

Notable disabled code:
- Older richer `MAP_MAGIC` file-map writer is commented out.
- Current `make_map` writes raw `saved_item` records instead.

Notable risks/quirks:
- Produces `scan.log` unconditionally.
- Regex uses basic `regcomp` flags.
- Some map code is marked as not working for long files.
- Raw saved-item serialization is not portable.
