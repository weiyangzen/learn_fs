# File Research: sources/local-fs/jfsutils/xpeek/directory.c

Implements directory listing and interactive display/edit traversal for JFS directory B-trees (`dtree`) and extent trees (`xtree`). This is one of the central metadata inspection files for `jfs_debugfs`.

Major commands:
- `directory(void)`: displays directory entries for an inode.
- `dtree(void)`: displays and optionally modifies the root directory tree stored in a directory inode.
- `xtree(void)`: displays and optionally modifies an inode extent tree, using `di_dirtable` for directories and `di_btroot` for non-directories.

Directory listing flow:
- Parses inode number and optional fileset, currently only fileset `0` for `directory`/`dtree`.
- Resolves the inode using `find_inode`.
- Reads the inode with `xRead`.
- Swaps disk endian representation with `ujfs_swap_dinode`.
- Verifies `IFDIR`.
- If the dtree root is a leaf, prints entries from root slots directly.
- If not a leaf, descends through internal dtree nodes to the leftmost leaf, then follows `header.next` across leaf pages.

Directory entry handling:
- `print_direntry(struct dtslot *, uint8_t)`: reconstructs multi-slot Unicode names from a leaf entry plus continuation slots, converts them to UTF-8 with `Unicode_String_to_UTF8_String`, and prints inode number plus name.
- Uses global `UTF8_Buffer[8 * JFS_PATH_MAX]`.

Dtree interactive display/edit:
- `dtree(void)` prints root dtree header fields including DASD limit/used, flags, `nextindex`, free list, `idotdot`, and slot table.
- Allows modification of selected root fields through shared `m_parse`.
- Writes modified inode back after swapping with `ujfs_swap_dinode(..., PUT)`.
- Uses `display_leaf_slots`, `display_internal_slots`, `display_slot`, and `display_extent_page` for traversal.

Xtree interactive display/edit:
- `xtree(void)` resolves an inode from filesystem, primary aggregate, or secondary aggregate inode table.
- Displays root xtree fields through `display_xtpage`.
- Allows modification of xtpage header fields and writes the containing inode back.
- Traverses leaf/internal XAD arrays with `display_leaf_xads` and `display_internal_xads`.
- Descends to non-root xtpage blocks with `display_internal_xtpage`.

Helper APIs:
- `display_xtpage(xtpage_t *)`: prints xtpage flags, `nextindex`, `maxentry`, and self PXD address.
- `display_leaf_slots(...)`: displays leaf directory entries and optional directory index field when `type_jfs & JFS_DIR_INDEX`.
- `display_internal_slots(...)`: displays internal dtree child extents and separator names.
- `display_slot(...)`: recursively prints continuation slots.
- `display_extent_page(int64_t)`: reads, displays, modifies, and writes a non-root dtree page.
- `display_leaf_xads(...)` / `display_internal_xads(...)`: display XAD extents and allow descent for internal pages.
- `display_internal_xtpage(xad_t)`: reads and edits a child xtpage.
- `strToUcs(...)`: simplistic byte-to-`UniChar` copy for modified names.

Integration points:
- Depends on `find_inode`, `xRead`, `xWrite`, `m_parse`, and `prompt`.
- Uses JFS structures/macros from `jfs_dtree.h`, `jfs_xtree.h`, `jfs_filsys.h`, `jfs_unicode.h`, and endian helpers.
- Uses global `type_jfs` to choose endian conversion and directory-index display behavior.

Notable behavior and risks:
- The interactive modification paths can corrupt on-disk directory and extent trees; validation is minimal.
- `strToUcs` is not a full UTF-8 to UCS converter; edits through it only copy byte values into `UniChar`.
- Several reads/writes assume metadata structure sizes and block mappings are valid.
- Some traversal command returns are overloaded as character actions (`u`, `d`, `x`) and can be hard to reason about.
- Duplicate prototype for `display_slot` appears near the top.
