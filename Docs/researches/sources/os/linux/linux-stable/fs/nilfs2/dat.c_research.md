# File Research: sources/os/linux/linux-stable/fs/nilfs2/dat.c

## Summary
Implements the NILFS disk address translation file. DAT maps virtual block numbers to physical block numbers and tracks checkpoint lifetimes for copy-on-write block replacement.

## Main Responsibilities
- Allocates, starts, ends, frees, and updates DAT entries.
- Translates virtual block numbers to physical blocks.
- Marks DAT entry blocks dirty.
- Frees vectors of virtual block numbers.
- Moves virtual blocks during garbage collection.
- Exports virtual block information to userspace.
- Reads and initializes the DAT metadata inode.

## Important Behavior
Each DAT entry contains `de_start`, `de_end`, and `de_blocknr`. Allocation initializes lifetime to `[1, ~0]` with no physical block. Starting an entry records the current checkpoint number and physical block. Ending an entry sets `de_end` either to the current checkpoint or to `de_start` for dead entries.

`nilfs_dat_prepare_end()` validates that entry lifetime does not start in the future and prepares bitmap freeing if the entry has no physical block. `nilfs_dat_commit_free()` detects missing allocator buffers as duplicate virtual block use and reports filesystem inconsistency.

`nilfs_dat_prepare_update()` combines ending an old virtual pointer and allocating a new one. `nilfs_dat_commit_update()` commits both halves and is used by B-tree/direct propagation.

`nilfs_dat_move()` updates the physical block associated with a virtual block for GC. Before changing the entry, it freezes the entry buffer into the metadata shadow map so normal translation outside GC can still see the committed mapping until the segment is safe.

`nilfs_dat_translate()` redirects to frozen buffers when not doing GC and the entry buffer has been redirected. This prevents readers from observing uncommitted GC move targets.

## Risks
DAT is central to NILFS virtual block consistency. Incorrect handling of redirected/frozen buffers can expose uncommitted physical blocks. Missing DAT entries are translated to `-EINVAL` by some callers to report bmap metadata corruption.
