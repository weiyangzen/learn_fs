# File Research: sources/os/linux/linux/fs/ocfs2/dir.c

## Purpose
Implements OCFS2 directory operations: lookup, validation, insertion, deletion, readdir, empty-dir checks, new directory initialization, inline-to-extent directory expansion, indexed directory creation/maintenance, free-space tracking, index splitting/rebalancing, and dx-index truncation.

## Directory Formats
The code supports:
- inline-data directories stored inside the dinode.
- extent-backed unindexed directories.
- indexed directories with a dx root and optional dx leaf blocks.
- directory block trailers for metadata ECC and indexed-directory free-list accounting.

`ocfs2_supports_dir_trailer()` and `ocfs2_new_dir_wants_trailer()` decide whether a directory block reserves trailing trailer space.

## Validation
The file validates:
- dirent record length, alignment, name length, and block bounds via `ocfs2_check_dir_entry()`.
- directory block ECC via `ocfs2_validate_dir_block()`.
- directory trailers via `ocfs2_check_dir_trailer()`.
- dx root and dx leaf signatures/ECC/layout via `ocfs2_validate_dx_root()` and `ocfs2_validate_dx_leaf()`.

Read helpers intentionally squash many read/validation failures to `-EIO` after logging.

## Lookup
`ocfs2_find_entry()` dispatches by format:
- inline: `ocfs2_find_entry_id()`
- extent/unindexed: `ocfs2_find_entry_el()` with readahead and wraparound search
- indexed: `ocfs2_find_entry_dx()`.

Indexed lookup hashes the name using TEA-derived ext3-style hashing, locates the correct dx root/leaf entry, then reads the referenced unindexed dirent block and confirms the actual name.

## Hashing and Index Mapping
`ocfs2_dx_dir_name_hash()` computes major/minor hash values using the filesystem dx seed. Major hash selects a dx cluster range; minor hash selects a block offset within the cluster using `osb_dx_mask`.

## Directory Entry Modification
- `ocfs2_update_entry()` changes an existing dirent’s inode and file type.
- `ocfs2_delete_entry()` dispatches deletion by format.
- `__ocfs2_delete_entry()` removes a dirent by merging record length into the previous entry or clearing inode when first.
- Indexed deletion also removes the corresponding dx entry and updates dx root entry counts and free-list trailer state.

## Insert Path
The public preparation/add flow is:
1. `ocfs2_prepare_dir_for_insert()` finds or creates a block with space and fills `ocfs2_dir_lookup_result`.
2. `__ocfs2_add_entry()` journals the needed buffers, optionally inserts a dx entry, splits an existing dirent if needed, writes the new dirent, recalculates indexed free-list state, updates mtime/ctime and i_version, and dirties buffers.

For indexed directories, preparation first ensures index capacity, may expand inline dx root to external leaves, searches the dx free list for unindexed dirent space, and extends the directory if needed.

## Readdir
`ocfs2_readdir()` takes the inode lock, updates atime, downgrades from EX to PR when possible, and calls `ocfs2_dir_foreach_blk()`. Iteration supports inline and extent-backed directories, handles i_version changes by rescanning to a safe dirent boundary, validates each emitted entry, and performs simple buffer-head readahead for extent directories.

## Empty Directory Check
`ocfs2_empty_dir()` uses a dir-context callback to verify `.` and `..` at expected offsets and detect any other entries. For indexed directories it first checks `dr_num_entries == 2`, then still scans the directory for dot/dotdot validation.

## New Directory Creation
`ocfs2_fill_new_dir()` selects:
- inline initialization if inline data is enabled on the inode.
- indexed directory initialization if filesystem supports indexed dirs.
- plain extent-backed initialization otherwise.

`ocfs2_fill_initial_dirents()` writes `.` and `..`. Extent-backed creation can initialize trailers. Indexed creation first builds an unindexed directory block, then attaches a dx root and indexes `.` and `..`.

## Inline-to-Extent Expansion
`ocfs2_expand_inline_dir()` converts an inline directory to extent-backed storage. It:
- reserves data and optional metadata/index allocations.
- handles quota accounting.
- copies inline dirents to a new block.
- expands the final dirent and initializes trailers.
- clears `OCFS2_INLINE_DATA_FL`.
- inserts data extents.
- optionally attaches and populates a dx index.
- returns lookup buffers needed to finish the pending insert.

The implementation carefully orders journal operations so partially completed conversion leaves consistent directory contents.

## Directory Extension
`ocfs2_extend_dir()` grows extent-backed directories by one block, allocating a new cluster when `i_size` reaches allocated clusters. It formats the new block as one empty dirent, initializes a trailer if needed, links it into indexed free-list state, updates size and inode blocks, and returns the new buffer.

## Indexed Directory Growth
Indexed directories use:
- inline dx root until root entry capacity is exhausted.
- external dx leaf clusters after `ocfs2_expand_inline_dx_root()`.
- `ocfs2_find_dir_space_dx()` to locate or rebalance a dx leaf.
- `ocfs2_dx_dir_rebalance()` to split full dx leaf clusters.

Rebalancing sorts a full leaf, chooses a split hash while handling same-major-hash corner cases, allocates/formats a new leaf cluster, inserts the extent, and transfers entries with major hashes greater than or equal to the split point.

## Free-Space Tracking
Directory block trailers maintain:
- largest free record length
- linked-list pointer for dx free list.

Insertion recalculates or removes a block from the free list. Deletion adds a block to the free list if it newly gains reusable space.

## Truncation and Index Removal
`ocfs2_dx_dir_truncate()` removes external dx index extents, then `ocfs2_dx_dir_remove_index()` clears `OCFS2_INDEXED_DIR_FL`, zeros `i_dx_root`, frees the dx root metadata bit, flushes truncate log work, and runs cached deallocations.

## Important Dependencies
This file is tightly coupled to OCFS2 allocation, journaling, inode locking, metadata ECC, extent maps, quota accounting, truncate/dealloc logic, and the VFS dir-context API.
