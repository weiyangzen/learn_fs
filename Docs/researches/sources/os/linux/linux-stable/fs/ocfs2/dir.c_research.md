# File Research: sources/os/linux/linux-stable/fs/ocfs2/dir.c

## Summary
Implements OCFS2 directory storage, lookup, mutation, iteration, indexed-directory support, inline-directory expansion, directory block trailers/checksums, free-space accounting, directory initialization, and directory index truncation. It handles three directory forms: inline data in the dinode, extent-backed unindexed directory blocks, and extent-backed indexed directories with a dx root and dx leaves.

## Main Responsibilities
- Validate and read directory blocks, directory trailers, dx roots, and dx leaves.
- Hash names for indexed directories using TEA-derived hashing and the filesystem dx seed.
- Lookup names in inline, unindexed extent-backed, and indexed directories.
- Add, update, and delete directory entries while journaling the correct dinode/data/index buffers.
- Maintain indexed directory entries, dx leaf blocks, root/leaf transitions, and free-space lists.
- Iterate directories for `readdir()` and internal scans.
- Check whether directories are empty for `rmdir`.
- Fill new directories with `"."` and `".."` in inline, extent, or indexed form.
- Expand inline directories into extent-backed directories and optionally attach indexes.
- Extend directory size and allocate new data/index clusters.
- Remove/truncate directory index metadata.

## Key Interfaces
- `ocfs2_find_entry()` returns a filled `ocfs2_dir_lookup_result` for name operations.
- `ocfs2_delete_entry()` removes a previously found dirent and corresponding dx entry if indexed.
- `__ocfs2_add_entry()` inserts a prepared dirent and updates dx metadata/free-list accounting.
- `ocfs2_update_entry()` changes the inode/type in an existing dirent.
- `ocfs2_prepare_dir_for_insert()` finds or creates space for a new name.
- `ocfs2_find_files_on_disk()` and `ocfs2_lookup_ino_from_name()` map names to inode block numbers.
- `ocfs2_readdir()` and `ocfs2_dir_foreach()` implement public and internal directory iteration.
- `ocfs2_fill_new_dir()` initializes a newly created directory.
- `ocfs2_dx_dir_truncate()` frees indexed-directory metadata.

## Important Behavior
Directory trailers are used when metadata ECC is enabled or directories are indexed. The trailer stores signature, parent dinode block, block number, free record length, and free-list linkage. Reads validate ECC first, then validate trailer identity when the directory format requires it. New blocks initialize trailers before being exposed to lookup or free-list code.

Lookup dispatches by directory type. Inline directories search the dinode inline-data area. Unindexed extent directories scan blocks with small readahead and remember `ip_dir_start_lookup` for the next search. Indexed directories read `i_dx_root`, hash the target name, locate the dx leaf through the dx root extent list, scan matching dx entries, and then search the referenced unindexed dirent block to confirm the actual name.

Deletion in indexed directories is a two-part operation. It journals the dx root and possibly dx leaf, deletes the unindexed dirent by merging/freeing records, recomputes the data block's largest free record, links the block into the indexed free list if it was not already there, decrements `dr_num_entries`, and removes the dx entry from its entry list.

Insertion is deliberately split. `ocfs2_prepare_dir_for_insert()` hashes the name when indexing is possible, ensures there is index capacity, finds a data block through the indexed free list or unindexed scan, and extends/expands the directory if needed. `__ocfs2_add_entry()` then journals the relevant buffers, splits an existing record if necessary, writes the new dirent, updates timestamps/version, inserts dx metadata, and recalculates free-list state.

Inline directory expansion is heavily ordered. The code allocates data and optional index storage, copies inline dirents into the first data block, expands the last record to the block/trailer boundary, initializes trailers, converts the dinode from inline data to an extent list, inserts the first data extent, attaches a dx root when supported, indexes existing records, and only then returns buffers for the pending insertion.

Indexed directories start with inline dx entries in the dx root when small. When the root fills, `ocfs2_expand_inline_dx_root()` allocates a leaf cluster, formats leaves, redistributes root entries by minor hash, clears the inline flag, and inserts the new dx extent. When a dx leaf fills, `ocfs2_dx_dir_rebalance()` sorts entries, chooses a split major hash, allocates a new cluster, inserts it in the dx extent tree, and transfers entries whose major hash belongs to the new range.

`readdir()` takes an inode lock with atime handling, may downgrade from EX to PR to reduce contention, then iterates only enough entries for one userspace call. Iterators use inode version checks to resynchronize offsets if the directory changed between calls.

## State and Synchronization
Directory metadata changes occur inside OCFS2 journal transactions. Allocation paths use `ip_alloc_sem`, quota reservations, allocation contexts, and extent-tree helpers. Inode dynamic features are changed under `ip_lock`. Readdir and name operations assume callers hold appropriate VFS inode semaphores and OCFS2 cluster locks; `ocfs2_readdir()` takes the inode lock itself.

## Cross-File Interactions
This file is central to OCFS2 namei and directory operations. It uses allocation/suballocation, extent maps and extent trees, journaling, block checksum validation, inode locking/state, quota accounting, truncate/deallocation, system file inode access, and dentry/namei code. The public structures and prototypes are in `dir.h`.

## Risks
Directory correctness depends on keeping unindexed dirent blocks and dx index entries in sync. Failures after one side is journaled can corrupt lookup unless transaction ordering is preserved. Trailer and free-list accounting must accurately reflect the largest free record or indexed insertion can miss available space or overwrite trailers. Hash split corner cases with identical major hashes can return `-ENOSPC` even during rebalance. Inline-to-extent conversion is particularly sensitive because it changes on-disk format, size, extents, optional index metadata, quota state, and returned insertion context in one operation.
