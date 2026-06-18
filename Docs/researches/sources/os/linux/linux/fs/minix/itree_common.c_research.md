# File Research: sources/os/linux/linux/fs/minix/itree_common.c

## Purpose
Provides the generic indirect-block tree implementation used by both Minix V1 and V2/V3 block mapping and truncation code. It is included directly by `itree_v1.c` and `itree_v2.c` after each wrapper defines block type, depth, direct-block count, endian conversion, and `block_to_path()`.

## Main Responsibilities
- Resolve logical file blocks through direct and indirect block chains.
- Allocate missing direct/indirect blocks for writes.
- Splice newly allocated branches into the inode tree safely.
- Detect concurrent truncation/modification and retry lookups.
- Free data blocks and indirect subtrees during truncation.
- Compute total blocks consumed by file data and indirect metadata.

## Key Types and State
- `Indirect` stores a pointer to a block pointer slot, its observed key, and the buffer containing it.
- `pointers_lock` protects updates and validation of indirect block pointer chains.
- The including file supplies `block_t`, `DEPTH`, `DIRECT`, `i_data()`, `block_to_cpu()`, `cpu_to_block()`, and `block_to_path()`.

## Key Functions
- `add_chain()` records an observed pointer slot and value.
- `verify_chain()` checks that all recorded pointer slots still contain their observed values.
- `get_branch()` walks a block pointer chain, reading indirect blocks and returning the first missing/failed link.
- `alloc_branch()` allocates a chain of blocks, initializes intermediate indirect buffers, and frees partial allocations on failure.
- `splice_branch()` atomically attaches a new branch after verifying the parent chain has not changed.
- `get_block()` implements Linux `get_block_t` behavior: map existing blocks or allocate on `create`.
- `find_shared()` finds the shared branch point for truncation and detaches the first subtree to free.
- `free_data()` frees contiguous data block pointers.
- `free_branches()` recursively frees indirect trees.
- `truncate()` releases blocks beyond `i_size`, including partial shared branches and whole indirect subtrees.
- `nblocks()` estimates data plus metadata block count for stat reporting.

## Data and Control Flow
`get_block()` first converts the logical block into offsets using version-specific `block_to_path()`. It calls `get_branch()` to traverse existing pointers. If all links exist, it maps the buffer head. If a link is missing and creation is requested, it allocates the remaining branch and attempts to splice it into the tree. If validation fails due to concurrent truncate or mutation, it frees the new branch and retries.

Truncation computes the first logical block beyond EOF, truncates partial page-cache data, then either frees direct blocks or finds the shared indirect chain. It detaches and frees no-longer-needed subtrees, marks changed metadata buffers dirty through Minix metadata buffer tracking, updates timestamps, and marks the inode dirty.

## Important Behaviors and Edge Cases
- `-EAGAIN` is used internally when a pointer chain changes during lookup/allocation; the algorithm retries.
- Failed allocation frees all blocks already allocated for the branch.
- Indirect metadata buffers are dirtied with `mmb_mark_buffer_dirty()` so Minix can sync metadata buffers on eviction/fsync.
- Truncation tolerates unreadable indirect blocks by skipping unreadable subtrees after clearing reachable pointers.
- The code assumes the including V1/V2 file defines compatible constants before inclusion.
- Whole-subtree freeing starts at `DIRECT` indirect roots after partial branch cleanup.

## Dependencies
- Minix block allocator/free routines: `minix_new_block()` and `minix_free_block()`.
- Buffer-head APIs: `sb_bread()`, `sb_getblk()`, `brelse()`, `bforget()`, buffer locking/dirtying.
- Inode timestamp and dirtying helpers.

## Research Notes
This file is a classic shared-C-include pattern: it is not independently compiled. Its behavior changes according to V1/V2 definitions supplied by the wrapper file. The locking model focuses on protecting pointer consistency, not broad inode serialization.
