# File Research: sources/os/linux/linux-stable/fs/ext4/indirect.c

This file implements legacy non-extent block mapping and space removal for ext4 inodes that use direct, indirect, double-indirect, and triple-indirect block pointers.

Major responsibilities:
- Block path lookup:
  - `ext4_block_to_path()` translates a logical block into offsets through direct/indirect/double/triple-indirect levels and reports boundary distance.
  - `ext4_get_branch()` reads and validates the indirect block chain, returning either a full chain or the first missing/failed link.
- Allocation goal and length:
  - `ext4_find_near()` chooses an allocation goal near the previous pointer, the containing indirect block, or the inode’s goal block.
  - `ext4_find_goal()` clamps the goal for non-extent 32-bit physical block limits.
  - `ext4_blks_to_allocate()` decides how many contiguous data blocks can be allocated without crossing indirect-block boundaries or existing mappings.
- Block allocation and insertion:
  - `ext4_alloc_branch()` allocates required indirect metadata blocks and data blocks, initializes new indirect blocks, links child pointers inside the new branch, journals create access, and frees all newly allocated blocks on failure.
  - `ext4_splice_branch()` journals the parent, installs the missing pointer, fills contiguous direct pointers when possible, dirties metadata or inode, and frees the new branch on splice failure.
  - `ext4_ind_map_blocks()` is the main non-extent implementation for `ext4_map_blocks()`: it looks up existing mappings, reports holes, allocates missing branches when requested, sets map flags, updates fsync transaction state, and releases indirect buffers.
- Transaction credit estimation:
  - `ext4_ind_trans_blocks()` estimates indirect metadata blocks touched for a contiguous mapping.
- Truncation support:
  - `ext4_ind_truncate_ensure_credits()` extends or restarts truncate transactions and reacquires write access as needed.
  - `ext4_ind_trunc_restart_fn()` dirties metadata/inode, discards preallocations, drops `i_data_sem` during transaction restart, and marks that the lock was dropped.
  - `ext4_find_shared()` finds partially shared branches at a truncate boundary.
  - `ext4_clear_blocks()`, `ext4_free_data()`, and `ext4_free_branches()` clear pointers, validate block ranges, accumulate contiguous frees, handle revoke/forget flags, free subtrees bottom-up, and journal parent metadata.
  - `ext4_ind_truncate()` removes all blocks beyond the inode size for non-extent files, updates extent status cache and `i_disksize`, handles direct/indirect/double/triple branches, and frees whole subtrees.
- Hole punching/range removal:
  - `ext4_ind_remove_space()` frees blocks in a logical range, handling direct-only ranges, ranges crossing levels, and same-level partial branches until start/end paths converge.

Important design points:
- Indirect mapping uses an `Indirect` chain of pointer location, key value, and buffer head to detect missing links and preserve references during updates.
- Allocation prepares the whole disconnected branch first, then atomically splices the final missing link, so failed allocation does not expose partial trees.
- Bigalloc is rejected for allocating non-extent inodes.
- Truncate frees data and indirect blocks bottom-up, using journal revoke/forget flags to prevent replay from resurrecting freed indirect blocks.
- Transaction restarts during truncate must temporarily drop `i_data_sem` to avoid deadlock with block mapping, then reacquire it.
- Pointers are cleared only after journal credit handling and block-range validation.

Key invariants:
- Allocation requires a non-null journal handle; lookup can run without one.
- Callers must hold `i_data_sem` for mapping: write mode when allocating, read mode when only looking up.
- `ext4_get_branch()` validates indirect block references after reading.
- Non-extent files cannot map blocks beyond legacy bitmap maxbytes semantics.
- Truncate and punch-hole logic must preserve blocks below the target range while freeing all complete right-hand subtrees.
- Invalid block references are reported as inode corruption and not freed blindly.
