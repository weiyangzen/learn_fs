# File Research: sources/os/linux/linux-stable/fs/ntfs3/attrib.c

This is the ntfs3 attribute storage engine. It manages resident and nonresident attribute sizing, cluster allocation/deallocation, runlist packing and loading, delayed allocation, sparse and compressed data mapping, WOF frame offset lookup, hole punching, range insertion/collapse, and forced conversion to nonresident storage.

Main responsibilities:
- Computes preallocation clumps and allocates clusters into `runs_tree` instances using volume free-space search.
- Deallocates run ranges, optionally issuing trim and removing delayed-allocation reservations.
- Converts resident attributes into nonresident attributes, preserving data through page cache or direct run writes.
- Resizes attributes through `attr_set_size_ex()`, handling resident growth/shrink, nonresident extension/truncation, delayed allocation, sparse/compressed files, MFT-specific allocation, preallocation, multi-segment attributes, and attribute-list creation/expansion.
- Resolves data blocks for read/write paths, including resident data, cached real runs, delayed allocation placeholders, sparse holes, compressed frames, and EOF.
- Allocates real clusters for sparse/compressed holes and updates packed runs and `total_size`.
- Reads WOF LZX/XPRESS frame offset tables when configured.
- Detects compressed frames by inspecting data and sparse runs within an NTFS compression unit.
- Rewrites compressed/sparse frame allocation with `attr_allocate_frame()`.
- Implements fallocate-like range operations: collapse range, punch hole, insert range, and force nonresident.

Important functions:
- `attr_load_runs()` and `attr_load_runs_vcn()` unpack on-disk run arrays into in-memory run trees.
- `run_deallocate_ex()` frees physical cluster ranges and keeps delayed allocation accounting synchronized.
- `attr_allocate_clusters()` wraps free-space search, run insertion, optional zeroout, partial allocation return, and rollback.
- `attr_make_nonresident()` removes a resident attribute record and reinserts it as nonresident with allocated runs.
- `attr_set_size_ex()` is the central resize routine for both `$DATA` and other attributes.
- `attr_data_get_block()` and `attr_data_get_block_locked()` serve mapping requests and allocate sparse/compressed holes when requested.
- `attr_load_runs_range()` ensures a byte range has run mappings loaded.
- `attr_wof_frame_info()` reads compressed WOF frame offset metadata for external compression.
- `attr_is_frame_compressed()` distinguishes uncompressed, sparse, and compressed NTFS compression frames.
- `attr_allocate_frame()` updates physical allocation for a compressed frame and maintains `total_size`.
- `attr_collapse_range()`, `attr_punch_hole()`, and `attr_insert_range()` mutate file layout for aligned ranges.
- `attr_force_nonresident()` converts default data to nonresident form.

Notable implementation details:
- Delayed allocation is represented with `ni->file.run_da` and `DELALLOC_LCN`; it is disabled for MFT, compressed/external attributes, and selected no-delalloc callers.
- Sparse and compressed attributes use `total_size` as physical allocation accounting distinct from logical `data_size` and `alloc_size`.
- Run packing with `mi_pack_runs()` can force creation of `$ATTRIBUTE_LIST` and additional nonresident attribute segments when one MFT record cannot hold the runlist.
- Many multi-step mutating paths have partial rollback; if rollback is impossible or metadata becomes inconsistent, the inode is marked bad with `_ntfs_bad_inode()`.
- Compressed/sparse range operations enforce cluster or compression-frame alignment and can return ntfs3-specific alignment errors.

Research notes:
- This file is one of the highest-risk ntfs3 metadata mutation points because it ties allocator state, runlists, MFT record layout, attribute-list entries, inode size, and VFS dirtying together.
- Several comments identify complexity and TODOs around merging allocation/resize paths, which aligns with the overlapping responsibilities of `attr_set_size_ex()`, `attr_data_get_block_locked()`, and `attr_allocate_frame()`.
