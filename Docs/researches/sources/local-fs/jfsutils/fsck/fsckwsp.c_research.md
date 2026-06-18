# File Research: sources/local-fs/jfsutils/fsck/fsckwsp.c

## Purpose
Implements the main in-memory and on-device workspace services used by `jfs_fsck`: dynamic workspace allocation, fsck block-ownership bitmap management, duplicate-block tracking, inode-record lookup tables, temporary buffers, tree queues, service-log buffers, and cleanup.

## Key Elements
Provides a custom arena-style allocator through `alloc_wrksp()` and `alloc_wsp_extent()`. Workspace extents are linked from `agg_recptr->wsp_extent_list`, rounded to 8-byte alignment, zero-initialized, and tagged for normal fsck use or `logredo` use. `release_logredo_allocs()` rewinds only logredo-tagged extents, and `workspace_release()` frees the very-large buffer plus all allocated workspace extents.

Manages the fsck block map through `establish_wsp_block_map_ctl()`, `establish_wsp_block_map()`, `blkall_increment_owners()`, `blkall_mark_free()`, `extent_record_dupchk()`, `extent_unrecord()`, and `process_extent()`. The block map is either backed by the aggregate’s reserved fsck workspace when write access is available or by dynamic storage in read-only mode. `process_extent()` bounds-checks extents against valid metadata/fileset block ranges and marks owning inode records for repair when extents are impossible or clipped.

Tracks multiply allocated blocks with a sorted doubly linked list of `struct dupall_blkrec`. `dupall_insert_blkrec()`, `dupall_find_blkrec()`, `blkall_split_blkrec()`, `extent_1stref_chk()`, and `extent_record_dupchk()` maintain duplicate ranges, owner counts, and unresolved first-reference counts. Inodes involved in unresolved duplicates are flagged for release or EA/ACL field clearing depending on where the bad extent came from.

Builds inode workspace structures for aggregate and fileset inodes. `establish_agg_workspace()` creates the aggregate inode map/table assumptions for release-1 JFS. `establish_fs_workspace()` reads the selected AIT extent, derives fileset IAG count, allocates fileset inode maps/tables, and sets up the initial root metadata record tables. `get_inorecptr()`, `inorec_agg_search_insert()`, `inorec_fs_search_insert()`, `get_inorecptr_first()`, and `get_inorecptr_next()` provide random and sequential inode-record access.

Also owns reusable queues/buffers: `treeQ_*` for xtree breadth-first traversal, `dtreeQ_*` for directory-tree processing, directory reconstruction buffers from the very-large buffer, EA buffer setup, temporary inode/node buffers, and fsck service-log lifecycle via `fscklog_start()`, `fscklog_init()`, and `fscklog_end()`.

## Dependencies
Uses global `sb_ptr`, `agg_recptr`, and `bmap_recptr` from `xchkdsk.c`; message emission from `message.h`; disk I/O helpers such as `ujfs_rw_diskblocks()`; endian conversion for fsck block-map pages; inode/AIT helpers such as `inode_get()` and `ait_special_read_ext1()`; and many constants/types from `xfsckint.h`.

## Behavior/Risks
The file is a central state manager. Most routines mutate global aggregate state rather than returning rich objects, so callers depend on side effects such as `corrections_needed`, `ignore_alloc_blks`, `selected_to_rls`, `dup_block_count`, and `unresolved_1stref_count`.

Duplicate-block handling is range-based but backed by a one-bit “already owned” block map plus a separate duplicate list for owner counts above one. Any boundary mistake in splitting duplicate records can affect later owner decrements and first-reference resolution.

`fsck_alloc_fsblks()` searches the workspace map page by page for contiguous free blocks, then records the chosen extent as allocated. It rejects allocations that would start in the reserved fsck workspace by comparing against `highest_valid_fset_datablk`.

The very-large buffer is deliberately reused for different phases (`EA`, directory buffers, inode extents), so correctness depends on phase ordering and `vlarge_current_use` discipline rather than independent ownership.
