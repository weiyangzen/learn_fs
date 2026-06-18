# File Research: sources/local-fs/jfsutils/xpeek/dmap.c

Implements interactive display and modification of the JFS aggregate block allocation map (`dmap`). It navigates from the block map inode to the dbmap control page, control pages at levels 0-2, dmap leaves, summary trees, and allocation bitmaps.

Main command:
- `dmap(void)`: reads aggregate block map inode `BMAP_I`, reads logical block 0 as `struct dbmap`, initializes `dmap_level` and `dmap_l2bpp`, then runs an action loop.

State/actions:
- `DISPLAY_DBMAP`: show top-level `struct dbmap`.
- `DISPLAY_CPAGE`: show a control page (`struct dmapctl`).
- `DISPLAY_LEAF`: show a dmap leaf (`struct dmap`).
- `DMAP_EXIT`: terminate.

Page mapping macros:
- `L1PAGE`, `L0PAGE`, and `DMAPPAGE` encode logical block numbers for the map tree layout.
- `decode_pagenum(...)` reverses logical page numbers into level-1, level-0, and dmap indexes.

Top-level control:
- `display_dbmap(...)` prints and edits map size, free count, AG geometry, preferred AG, AG free counts, and related fields.
- `display_agfree(...)` paginates/modifies the `dn_agfree` array.
- Writes back after endian swapping with `ujfs_swap_dbmap`.

Control pages:
- `display_cpage(...)` reads a mapped logical block through `ujfs_rwdaddr`, displays `nleafs`, `l2nleafs`, `leafidx`, `height`, and `budmin`.
- Supports modifying fields, going up, left/right sibling navigation, or entering the summary tree.

Dmap leaves:
- `display_leaf(...)` displays dmap leaf metadata, summary tree, working map (`wmap`), and persistent map (`pmap`).
- Uses `display_map` from `iag.c` for bitmap array editing.
- Supports sibling navigation and parent navigation.

Summary tree:
- `display_tree(...)` prints a small visual tree rooted at a selected top level/index.
- Supports back, descend to child page/leaf, goto, modify tree value, right/left, up, and exit.
- Marks `changed` when `stree` entries are edited so callers can write back the containing page.

Integration points:
- Depends on `find_inode`, `xRead`, `xWrite`, `ujfs_rwdaddr`, and `display_map`.
- Uses structures from `jfs_dmap.h`, `jfs_filsys.h`, and endian helpers.
- Uses global `type_jfs`, `bsize`, and `l2bsize`.

Notable behavior and risks:
- Modification paths have little semantic validation; incorrect map values can make allocation metadata inconsistent.
- `display_leaf` edits scalar dmap fields but returns to redisplay without immediately writing unless changes occur through subtree/map paths; scalar modifications rely on subsequent flow and may not persist as obviously as other paths.
- `display_tree` has hardcoded `tree_offset[6]` and accepts only heights 1-5.
- Several navigation paths assume fixed `LPERCTL` fanout and may not validate whether the logical target page exists in a smaller aggregate.
