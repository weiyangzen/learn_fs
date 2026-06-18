# File Research: sources/local-fs/jfsutils/fsck/dirindex.c

This module validates and updates the optional JFS directory index table used for indexed directory cookies. It depends on fsck globals `sb_ptr` and `agg_recptr`, disk I/O through `ujfs_rw_diskblocks`, extent lookup through `xTree_search`, endian helpers, and directory-table structures from the fsck/JFS headers.

The module keeps a small in-memory LRU cache of directory index pages. `NUM_INDEX_BUFS` is 16, and each `dir_index_page` tracks the aggregate address, next/previous LRU pointers, a dirty flag, and an array of 512 `dir_table_slot` entries. `allocate_dir_index_buffers()` allocates the cache, initializes a free list, and reports `MSG_OSO_INSUFF_MEMORY` on allocation failure.

`read_index_page()` maps a directory cookie to the corresponding directory-index page. It computes the byte offset from `(cookie - 2) * sizeof(struct dir_table_slot)`, derives the logical block number, searches the inode xtree, and reads the page from disk if it is not already cached. Cache hits are moved to MRU position. On cache eviction, dirty LRU pages are written with `write_index_page()` before reuse. I/O failures return `NULL` and recycle the page to the free list.

`flush_index_pages()` writes all dirty cached index pages and clears their dirty flags, returning the first write error. `dirty_index_page()` marks the most recently used page dirty and prints a diagnostic if called for a table pointer that is not the MRU page. That diagnostic is informal and not routed through fsck messages.

`verify_dir_index()` checks an observed directory entry’s cookie against the index table. It ignores cookie zero for compatibility with runtime repair expectations, rejects cookies below 2 or at/above `di_next_index`, selects inline `di_dirtable` when small enough, otherwise reads the external index page, and verifies that the slot is active, points at the expected directory-tree slot, and stores the expected leaf page address. On mismatch it disables further index checking for the inode, requests dirtable rebuild, and marks aggregate corrections needed.

`modify_index()` updates an index slot after directory-tree mutation. For inline tables it updates the inode’s `di_dirtable`; for external tables it reads the relevant index page, changes address and slot number, and marks the cache page dirty. Invalid cookies and read failures are silently ignored.

The module is tightly coupled to `fsckdire.c`: directory insert/split/delete code calls `modify_index()` when sorted-table positions change or entries move to new pages. Its main risk area is cache consistency: dirty pages must be flushed by the caller, and the dirty marker assumes the modified table is the MRU page returned by the last `read_index_page()`.
