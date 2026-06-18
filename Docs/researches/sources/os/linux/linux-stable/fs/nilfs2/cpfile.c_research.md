# File Research: sources/os/linux/linux-stable/fs/nilfs2/cpfile.c

## Summary
Implements the NILFS checkpoint file. It stores checkpoint entries, exports checkpoint and snapshot information, creates and finalizes checkpoints, deletes checkpoints, and maintains the on-disk doubly linked snapshot list.

## Main Responsibilities
- Computes checkpoint block offsets and entry offsets.
- Initializes checkpoint blocks with invalid entries.
- Reads checkpoint records into root and ifile state.
- Creates and finalizes checkpoint entries.
- Deletes single checkpoints or checkpoint ranges.
- Lists checkpoints and snapshots for userspace.
- Converts checkpoints to snapshots and snapshots back to checkpoints.
- Reports checkpoint statistics and reads the cpfile inode.

## Important Behavior
Checkpoint number 0 is invalid. Checkpoint blocks reserve initial space for the cpfile header by using `mi_first_entry_offset`. Non-header checkpoint blocks maintain a valid-checkpoint count in their first checkpoint-sized slot so empty blocks can be deleted.

`nilfs_cpfile_create_checkpoint()` creates or reuses a checkpoint entry, clears invalid state, updates valid counts and header checkpoint totals, and forces the entry block dirty. `nilfs_cpfile_finalize_checkpoint()` fills counts, block increment, creation time, checkpoint number, minor flag, and a serialized copy of the ifile inode and bmap.

`nilfs_cpfile_delete_checkpoints()` skips snapshots, invalidates normal checkpoints, updates counters, and deletes empty checkpoint blocks. If any snapshot is encountered in the requested range it returns `-EBUSY` after processing eligible normal checkpoints.

Checkpoint listing scans existing metadata blocks via `nilfs_mdt_find_block()`. Snapshot listing follows the header-owned doubly linked list and uses `~0ULL` as a terminator for continuation state.

Snapshot mode changes update neighboring list entries plus header snapshot counters under `mi_sem`. `nilfs_cpfile_change_cpmode()` refuses to clear snapshot mode for a checkpoint currently mounted as a snapshot.

## Risks
Snapshot list correctness depends on multiple checkpoint/header blocks being updated together. Invalid or missing checkpoint blocks during reads are treated as metadata corruption or invalid checkpoint requests. Deleting checkpoint ranges can partially succeed before returning `-EBUSY` because snapshots are preserved.
