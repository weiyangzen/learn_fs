# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_list.c

Implements listing of XFS extended attributes across shortform, leaf, and node formats with cursor-based continuation.

Key elements:
- `xfs_attr_shortform_compare` sorts shortform entries by hash then entry number.
- `xfs_attr_shortform_list` lists local shortform attrs directly when the output buffer can hold all entries; otherwise builds and sorts a temporary hash array to support stable cursor continuation.
- `xfs_attr_node_list_lookup` descends the attr btree from root to the leaf covering the cursor hash, validating node/leaf magic, levels, headers, and child pointers.
- `xfs_attr_node_list` validates or resynchronizes a cursor block, then walks leaf blocks in forward order until the output callback says enough or leaves run out.
- `xfs_attr3_leaf_list_int` lists entries from one leaf block, handles cursor duplicate counts, skips incomplete entries unless allowed, extracts local or remote names/value lengths, validates names, and calls the output callback.
- `xfs_attr_leaf_list` lists a single root leaf.
- `xfs_attr_list_ilocked` dispatches based on attr fork format: no attrs, shortform, single leaf, or node tree.
- `xfs_attr_list` handles shutdown check, stats, shared attr map locking, and unlock.

Dependencies:
- Uses attr fork formats, shortform parsing, attr leaf/node readers, hash calculation, name validation, and health marking.
- Output is callback-driven via `xfs_attr_list_context::put_listent`.

Research notes:
- Shortform attrs are not stored hash-sorted, so partial listings require a temporary sorted array.
- Cursor validation is defensive; invalid cursor blocks cause lookup from the btree root.
- Corrupt attr names, bad magic, impossible tree levels, or root backreferences mark the attr fork sick and return `-EFSCORRUPTED`.
- `bufsize == 0` is treated as a search-callback mode and avoids unnecessary sorting.
