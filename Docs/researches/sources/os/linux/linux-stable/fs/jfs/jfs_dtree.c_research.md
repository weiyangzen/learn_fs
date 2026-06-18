# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.c

This file implements the JFS directory B+-tree manager: lookup, insertion, deletion, rename-target modification, directory traversal, persistent directory cookies, root/page validation, page splitting, page extension, and transaction logging support for directory pages.

Key responsibilities:
- Implements directory lookup in `dtSearch()`, descending the dtree from the inline root through internal pages to a leaf while maintaining a `btstack` for later insert/delete propagation.
- Supports JFS OS/2 case-insensitive behavior by uppercasing search keys and comparing folded leaf names while preserving original names in leaf entries.
- Maintains the persistent directory index table used for stable `readdir()` cookies when `JFS_DIR_INDEX` is enabled. The table starts inline in `i_dirtable`, then migrates to an xtree-backed external table as it grows.
- Adds, frees, reads, and updates directory index entries through `add_index()`, `free_index()`, `read_index()`, and `modify_index()`.
- Inserts directory leaf entries in `dtInsert()`, allocating slot chains for variable-length Unicode names and updating the sorted entry table.
- Handles full-page insertions through `dtSplitUp()`, `dtSplitPage()`, `dtSplitRoot()`, and `dtExtendPage()`, including child extent allocation, quota accounting, sibling links, router-key generation, and directory index table repair after entries move.
- Deletes leaf entries in `dtDelete()` and propagates empty-page removal upward through `dtDeleteUp()`, including extent free logging, quota release, sibling relinking, and root reinitialization.
- Updates the inode number in an existing directory entry through `dtModify()`, used by rename-style operations.
- Implements `jfs_readdir()`, including modern persistent-index traversal, legacy OS/2 offset traversal, dot/dotdot emission, NLS conversion from JFS Unicode names, page-buffer batching before `dir_emit()`, and opportunistic repair of missing directory indices.
- Provides low-level entry manipulation helpers: `dtInsertEntry()`, `dtMoveEntry()`, `dtDeleteEntry()`, `dtTruncateEntry()`, `dtLinelockFreelist()`, `dtCompare()`, `ciCompare()`, `dtGetKey()`, and `ciGetLeafPrefixKey()`.
- Validates inline roots and regular directory pages with `check_dtroot()` and `check_dtpage()` before trusting freelists, sorted-entry tables, and slot indices.

Important interactions:
- Uses B+-tree/metapage helpers from `jfs_btree.h` and `jfs_metapage.h`; directory page 0 is the inline root stored in the inode.
- Uses the block allocator and xtree code when directory pages, directory-index pages, or relocated/extending pages need new physical storage.
- Uses the transaction manager heavily through `txLock()`, `txMaplock()`, `txLinelock()`, line locks, map locks, and `BT_MARK_DIRTY()` so dtree changes are journaled at slot granularity.
- Uses quota helpers for directory page allocation/free and directory extent extension.
- Uses Unicode helpers for little-endian UCS name storage, case folding, and codepage conversion during lookup and readdir.
- Cooperates with `diWrite()` through inode-private dtree and dirtable commit flags; inline directory roots and inline directory tables are copied back into dinodes during inode commit.

Notable invariants and risks:
- Directory entries are stored as linked chains of 32-byte slots; `freelist`, `freecnt`, `stblindex`, `nextindex`, and every slot `next` pointer must stay mutually consistent.
- Internal/router entries store child extents and possibly suffix-compressed keys; the leftmost internal key is intentionally treated as a minimum sentinel.
- Leaf entry layout differs for legacy directories versus indexed directories because indexed entries reserve space for a persistent directory-table index.
- Split and extension paths must update directory-table slots whenever leaf entries move to a different page or sorted-entry-table index.
- `jfs_readdir()` has two independent offset schemes: persistent index cookies for indexed directories and `(page-number,index)` legacy offsets for old directories.
- The code has many paired metapage pins/releases and transaction locks; error paths in split/extend/delete flows are especially sensitive to leaked pins, double frees, stale quota accounting, and partially updated sibling links.
- The page validation helpers reduce corruption exposure by rejecting invalid freelists, duplicate slot references, bad sorted-table entries, and impossible free counts before page use.

Research notes:
- This is the core JFS pathname-directory engine. The most important local design is the combination of a sorted slot table for B+-tree search, variable-length slot chains for names, and a separate persistent directory index table for stable VFS/NFS directory positions.
