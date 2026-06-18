# File Research: sources/os/linux/linux/fs/ext4/indirect.c

Implements block mapping, allocation, truncation, and hole punching for non-extent ext4 inodes using traditional direct/indirect block pointers.

Key behavior:
- Defines `Indirect`, a cached pointer-chain entry containing the pointer location, stored key, and backing buffer.
- `ext4_block_to_path()` maps a logical block to direct, single-indirect, double-indirect, or triple-indirect offsets.
- `ext4_get_branch()` walks an indirect pointer chain, reads indirect blocks, validates block references, and stops at holes or I/O/corruption errors.
- Allocation locality helpers:
  - `ext4_find_near()` prefers a previous neighboring pointer, then the indirect block location, then the inode’s goal block.
  - `ext4_find_goal()` limits goals to the 32-bit physical range used by non-extent files.
- `ext4_blks_to_allocate()` counts how many data blocks can be allocated contiguously within the current indirect boundary/hole.
- `ext4_alloc_branch()` allocates needed indirect blocks plus data blocks, initializes newly allocated indirect buffers, links child pointers in memory, and frees all new blocks on failure.
- `ext4_splice_branch()` journals the parent pointer, splices the newly allocated branch into the inode/indirect tree, fills contiguous direct mappings when possible, and dirties either the parent indirect block or inode.
- `ext4_ind_map_blocks()`:
  - looks up existing non-extent mappings
  - reports hole length for lookup-only requests
  - rejects block allocation for non-extent inodes on bigalloc filesystems
  - allocates missing indirect/data branches when requested
  - returns mapped length, physical block, new/mapped/boundary flags, and updates fsync transaction state
- `ext4_ind_trans_blocks()` estimates indirect metadata blocks touched by mapping contiguous blocks.
- Truncation credit helpers restart transactions when needed and temporarily drop `i_data_sem` safely.
- `ext4_find_shared()` identifies partially truncated indirect branches around the truncation boundary.
- `ext4_clear_blocks()` validates ranges, zeroes pointer slots, and frees contiguous blocks with correct metadata/forget flags.
- `ext4_free_data()` coalesces contiguous leaf block runs before freeing.
- `ext4_free_branches()` recursively frees indirect subtrees bottom-up, writes revoke/forget records for indirect metadata blocks, and clears parent pointers.
- `ext4_ind_truncate()` removes all blocks beyond inode size, updates `i_disksize`, removes extent-status cache entries, frees partial branches, and clears whole indirect subtrees.
- `ext4_ind_remove_space()` frees an arbitrary logical block range for punch-hole style operations, handling direct-only ranges, cross-level ranges, same-level ranges, partial branches, and whole subtrees.

Important interactions:
- Used only for inodes without `EXT4_INODE_EXTENTS`.
- Requires `i_data_sem`: write lock for allocation/truncate/punch, read lock for lookup.
- Coordinates with JBD2 metadata access, revoke/forget handling, preallocation discard, extent-status cache invalidation, and ext4 block allocator/freeing paths.
