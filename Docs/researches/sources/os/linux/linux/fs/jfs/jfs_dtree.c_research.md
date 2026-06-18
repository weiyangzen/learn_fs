# File Research: sources/os/linux/linux/fs/jfs/jfs_dtree.c

## Role

Implements the JFS directory B+tree manager, including lookup, insertion, deletion, rename-target modification, directory traversal, persistent directory cookies, and structural validation of directory tree pages.

## Key Responsibilities

- Searches directory B+trees in `dtSearch()`, including case-insensitive OS/2 ordering, internal router keys, leaf-name comparison, stale-inode checks for remove/rename, and returning pinned leaf search results through a `btstack`.
- Inserts leaf entries in `dtInsert()` and handles overflow through `dtSplitUp()`, `dtSplitRoot()`, `dtSplitPage()`, and `dtExtendPage()`.
- Uses variable-length directory names stored across 32-byte slots, with page-local sorted-entry tables (`stbl`) for binary search and insertion ordering.
- Maintains persistent directory entry indices when `JFS_DIR_INDEX` is enabled: inline table first, then an xtree-backed directory table after `MAX_INLINE_DIRTABLE_ENTRY`.
- Allocates, frees, reads, and updates directory index table slots through `add_index()`, `free_index()`, `find_index()`, `read_index()`, `modify_index()`, and `lock_index()`.
- Deletes entries in `dtDelete()` and propagates empty-page removal upward through `dtDeleteUp()`, including sibling relinking and extent/quota release.
- Initializes empty directory roots in `dtInitRoot()`, resetting inline or external directory index state as needed.
- Implements `jfs_readdir()` for both persistent-index directories and legacy OS/2/Linux JFS directory offsets.
- Repairs missing directory entry indices on writable filesystems via `add_missing_indices()` when `jfs_readdir()` detects invalid per-entry index values.
- Updates a directory entry inode number in `dtModify()` for rename operations.
- Provides low-level helpers for key extraction/comparison, suffix-compressed router key generation, entry insertion/move/delete/truncation, and transaction line locking.
- Validates in-inode dtree roots and external dtree pages with `check_dtroot()` and `check_dtpage()`.

## Important Interactions

- Uses generic JFS B+tree/metapage macros (`BT_GETPAGE`, `BT_MARK_DIRTY`, `BT_PUTPAGE`) specialized through `DT_GETPAGE`, `DT_PAGE`, and `DT_GETSTBL`.
- Relies on transaction locks from `jfs_txnmgr` for physical-image logging of dtree slots, stbl regions, root updates, relinks, extent frees, and directory index table updates.
- Allocates and frees directory data extents through `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `xtInsert()`, and `xtTruncate()`.
- Charges and releases quota blocks through `dquot_alloc_block()` and `dquot_free_block()` when directory pages or directory index pages are allocated/freed.
- Uses Unicode helpers for UCS-2 name comparison, uppercasing, and conversion to Linux directory entry names.
- Stores the inline root and inline directory table in `struct jfs_inode_info`; when the directory table grows, the same inode union area becomes an xtree root for external table pages.
- Calls `jfs_error()` on detected structural corruption so the filesystem can be marked for repair.

## Invariants and Risks

- Directory pages are slot-managed: `freecnt`, `freelist`, `nextindex`, and `stbl` must remain mutually consistent or lookup/readdir can walk invalid slots.
- External `dtpage_t` validation is performed when pages are fetched through `DT_GETPAGE`; corrupt pages return `-EIO`.
- Root pages are inline in the dinode and are never freed; empty-root deletion resets the root through `dtInitRoot()`.
- The leftmost internal router entry may have zero key length and is treated as less than any search key.
- Persistent directory indices must track leaf page block number and stbl position whenever entries are inserted, deleted, moved by split, or moved by stbl shifts.
- The readdir cookie space reserves `0`/`1` internally for `.`/`..` and returns one greater for NFSv4 compatibility.
- Legacy directories use packed `(pn,index)` offsets and do not have persistent indices.
- Split propagation keeps several metapages pinned across child and parent updates; every error path must release pins and free unused preallocated extents.
- Case-insensitive ordering folds search keys and leaf names for comparison but stores leaf names in original case.
- `add_missing_indices()` is a runtime mitigation for fsck gaps, especially `lost+found`, but cannot repair read-only mounts.
