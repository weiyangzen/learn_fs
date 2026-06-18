# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_lookup.c

This file implements directory reading, pathname lookup, directory block scanning, directory entry insertion/removal/rewrite, empty-directory checks, and rename ancestry checks for DragonFlyBSD ext2.

Key responsibilities:
- Convert ext2 directory entries to DragonFly `dirent` records for `readdir`.
- Resolve pathname components through htree lookup or linear directory scans.
- Track insertion/removal offsets in directory inode fields (`i_offset`, `i_count`, `i_endoff`, `i_diroff`).
- Validate directory entries and report/panic on corruption depending on mount writability.
- Insert new entries into fresh blocks or compacted free slots.
- Remove and rewrite directory entries.
- Check directory emptiness and prevent invalid directory rename ancestry.

Important functions:
- `ext2_readdir`: Iterates directory blocks, validates record progress, converts inode/type/name fields, emits cookies, and updates EOF state.
- `ext2_lookup` / `ext2_lookup_ino`: Main lookup implementation with create/rename/delete slot accounting, htree fallback, lock handling, sticky-directory checks, and parent handling.
- `ext2_search_dirblock`: Scans one directory block, validates entries, finds name matches, and accumulates free/compactable slots.
- `ext2_dirbad` / `ext2_check_direntry`: Directory corruption reporting and validation.
- `ext2_add_first_entry`: Writes an entry into a fresh directory block, including checksum tail support.
- `ext2_direnter`: Builds the new ext2 directory entry and inserts it.
- `ext2_add_entry`: Compacts an existing slot range, inserts the new entry, updates checksum, and writes the block.
- `ext2_dirremove`: Removes an entry by zeroing first entry or merging with previous record.
- `ext2_dirrewrite`: Repoints an existing entry and updates file type.
- `ext2_dirempty`: Accepts only `.` and matching `..`.
- `ext2_checkpath`: Walks `..` to prevent moving a directory into its descendant.

Important interactions:
- Uses `ext2_blkatoff`, `ext2_htree_lookup`, `ext2_truncate`, and directory checksum helpers.
- Directory entry file types are translated using local `FTTODT` and `DTTOFT` tables.

Notable behavior and risks:
- HTree lookup is active, but HTree insertion/index creation in `ext2_direnter` is inside `#if 0` because of documented lost dirents.
- On writable mounts, `ext2_dirbad` panics for corrupted directories; read-only mounts emit an SDT probe.
- Metadata checksum tails are treated as unavailable space during slot accounting.
