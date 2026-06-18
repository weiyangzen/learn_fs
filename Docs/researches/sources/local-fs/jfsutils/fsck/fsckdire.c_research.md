# File Research: sources/local-fs/jfsutils/fsck/fsckdire.c

This module is the fsck-side directory B+tree manager, derived from JFS `dtree.c`. It provides directory search, insert, delete, page split, page free, key comparison, entry movement, and root initialization routines used while fsck reconstructs or adjusts directories. It operates on `struct dinode` directory trees and uses fsck-specific page buffer/allocation helpers such as `recon_dnode_get()`, `recon_dnode_put()`, `recon_dnode_assign()`, `recon_dnode_release()`, `fsck_alloc_fsblks()`, and `fsck_dealloc_fsblks()`.

The file defines a small traversal stack (`btstack`) of up to `MAXTREEHEIGHT` frames, with macros to clear, push, pop, retrieve search results, and get/put B+tree pages. Root page block number is represented by zero and maps to the inline inode `di_btroot`; non-root pages are fetched through reconstruction dnode buffers. `DO_INDEX()` checks `JFS_DIR_INDEX` in the superblock and enables directory-index maintenance.

`fsck_dtSearch()` searches a directory tree for a Unicode component name. It uppercases the search key for OS/2 case-insensitive directories, descends from root through internal pages with binary search, maintains the traversal stack for later insert/delete propagation, and returns a pinned leaf page plus entry index. For create, an existing leaf hit returns `EEXIST`; for remove, a miss returns `ENOENT` and an inode mismatch returns `ESTALE`.

`fsck_dtInsert()` searches for the insertion position, computes required leaf slots using indexed or legacy leaf sizing, and either inserts directly with `dtInsertEntry()` or calls `dtSplitUp()` when the target leaf lacks space. New leaf data stores the target inode number.

`dtSplitUp()` propagates insertion splits bottom-up. Root leaf splits allocate a full page, call `dtSplitRoot()`, and update directory size. Non-root splits preallocate enough page extents for the maximum possible split cascade, call `dtSplitPage()` on the leaf, then walks parent frames. It computes router keys for new right pages, including suffix-compressed uppercase prefix keys between adjacent leaf pages where safe, inserts router entries into parents, and recursively splits full parents. Unused preallocated extents are deallocated on exit.

`dtSplitPage()` splits a non-root directory page. It allocates/assigns the new right page, sets sibling links, initializes sorted-table and freelist state, handles sequential append as a cheap right-page creation, updates the next sibling’s previous pointer for middle splits, computes a fill split point, moves entries to the right page with `dtMoveEntry()`, and inserts the pending entry on the correct side. When directory indexing is enabled, entries moved to the right page have their directory index slots updated through `modify_index()`. It increments `di_nblocks`.

`dtSplitRoot()` moves the inline root contents into a newly allocated child page and converts the inline root into an internal root with a single router entry. It copies the old sorted table and data area, initializes free slots, updates directory index table entries if the moved root was a leaf, inserts the pending new entry into the child page, resets the inline root header, and increments `di_nblocks`.

`fsck_dtDelete()` searches for a leaf entry to remove. If the page would become empty, it calls `fsck_dtDeleteUp()`; otherwise it frees the entry with `fsck_dtDeleteEntry()`, updates directory index entries whose sorted-table indices shifted, and releases the page.

`fsck_dtDeleteUp()` frees empty non-root pages and propagates router-entry deletion up the tree. It keeps an empty root by reinitializing it with `fsck_dtInitRoot()`, relinks siblings around deleted non-root pages with `dtRelink()`, deallocates backing extents, releases reconstruction buffers, and continues upward while parent pages become empty. It decrements `di_nblocks` for freed pages and reduces `di_size`.

`dtRelink()` updates neighboring directory pages’ `prev` and `next` pointers when a page is removed.

`fsck_dtInitRoot()` initializes an inline directory root as `DXD_INDEX | BT_ROOT | BT_LEAF`, clears entries, builds the freelist, sets free count, stores the `..` inode number in `idotdot`, and sets `di_size` to inline data size.

`dtCompare()` and `ciCompare()` compare search keys against leaf/internal entries, including multi-slot segmented names. `ciCompare()` uppercases stored characters when OS/2 case-insensitive behavior is active. `ciGetLeafPrefixKey()` computes a minimal distinguishing router prefix between adjacent leaf entries for suffix compression. `dtGetKey()` reconstructs a full component key from a directory entry’s segmented slots.

`dtInsertEntry()` allocates slots from a page freelist, writes leaf or internal entry data, copies name segments, terminates the segment chain, shifts the sorted table for middle insertions, and updates directory-index slots for shifted leaf entries when indexing is enabled. New indexed leaf entries initially get index zero until the caller creates or updates index state.

`dtMoveEntry()` moves sorted entries from a source page to a destination page during split, copying head and continuation slots, freeing source slots back to the source freelist, and updating destination sorted table, freelist, free count, and nextindex.

`fsck_dtDeleteEntry()` frees all slots belonging to a leaf/internal entry, returns them to the page freelist, shifts the sorted table left, and decrements `nextindex`.

This file is mutation-heavy and depends on careful invariants: sorted-table order, freelist integrity, segmented Unicode name layout, sibling links, `di_size`/`di_nblocks`, and optional directory-index cookie synchronization. The fsck-specific difference from live filesystem code is that it performs reconstruction against fsck buffers and explicit block allocation/deallocation helpers rather than journaled kernel transaction state.
