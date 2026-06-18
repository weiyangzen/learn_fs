# File Research: sources/os/linux/linux-stable/fs/minix/itree_common.c

## Purpose

Provides the shared indirect-block tree implementation included by MINIX V1 and V2/V3 block mapping files. It handles logical-to-physical block lookup, branch allocation, atomic splice into inode metadata, truncation, and block-count estimation.

## Main Entry Points

- `get_block()`: maps a logical block to a disk block, optionally allocating missing blocks.
- `truncate()`: frees blocks beyond `inode->i_size`.
- `nblocks()`: estimates total data plus metadata blocks for stat accounting.
- `get_branch()`: walks direct/indirect pointers and detects races.
- `alloc_branch()`: allocates and initializes a missing chain of indirect/data blocks.
- `splice_branch()`: installs a newly allocated branch after verifying the parent chain.
- `find_shared()` / `free_branches()` / `free_data()`: locate and free truncation targets.

## Control Flow And State

`get_block()` computes version-specific offsets through `block_to_path()`, walks the pointer chain with `get_branch()`, and either maps the existing block or allocates the missing suffix. Allocation builds indirect buffers bottom-up, zeroes them, records metadata buffers through `mmb_mark_buffer_dirty()`, and frees all partial work on failure. `splice_branch()` takes `pointers_lock`, verifies the chain has not changed, installs the new pointer, updates ctime, and marks the inode or indirect block dirty. Races with truncate return `-EAGAIN` and restart lookup.

Truncation converts file size to the first block to keep, truncates partial page data, finds any shared indirect branch that must be split, clears and frees the right-hand side, then frees whole remaining indirect subtrees from the inode’s direct indirect pointers. It updates mtime/ctime and marks modified metadata dirty.

## Dependencies

This file is a template and relies on the including file to define `DEPTH`, `DIRECT`, `block_t`, `block_to_cpu()`, `cpu_to_block()`, `i_data()`, and `block_to_path()`. It calls MINIX block allocator/free routines, buffer-head I/O, inode dirtying, `block_truncate_page()`, and `mapping_metadata_bhs` helpers.

## Risks

The code is concurrency-sensitive: pointer-chain verification, truncate races, and branch splicing all rely on `pointers_lock` and retry behavior. Failed branch allocation must free both newly allocated disk blocks and buffer heads. Lost metadata dirtying would leak or orphan indirect blocks after crash or writeback.
