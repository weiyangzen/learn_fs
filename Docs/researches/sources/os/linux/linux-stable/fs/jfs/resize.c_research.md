# File Research: sources/os/linux/linux-stable/fs/jfs/resize.c

## Purpose

Implements online JFS filesystem growth through `jfs_extendfs()`. It recalculates filesystem, fsck workspace, and inline log layout for a larger logical volume, extends allocation maps, optionally moves the inline log, and finalizes the new geometry in the superblocks.

## Main Flow

- Determines the old logical-volume end from inline log or fsck workspace descriptors and returns early if the volume did not grow.
- Validates the requested size against the block device or by probing the last requested block.
- Rejects growth on a read-only filesystem.
- Computes a new inline log size/address when applicable, computes fsck workspace size/address, and derives the new filesystem size. Shrinking is rejected.
- Formats a non-overlapping new inline log early when possible.
- Calls `txQuiesce()` before moving active log structures or updating allocation maps.
- If using inline log, shuts down the old log, marks `FM_EXTENDFS` in the on-disk superblock, stores transitional descriptors, formats and initializes the new log.
- Extends the block map with `dbExtendFS()`, grows the bmap file with `xtAppend()` if more dmap pages are needed, and finalizes via `dbFinalizeBmap()`.
- Extends/syncs the inode allocation map with `diExtendFS()` and `diSync()` when allocation-group sizing changed.
- Writes bmap state, copies the primary bmap inode to the secondary, updates primary and secondary superblocks, clears `FM_EXTENDFS`, and resumes transactions.

## Crash Recovery Model

The code uses `FM_EXTENDFS` and staged superblock descriptor updates so recovery/fsck can distinguish pre-extension, in-progress extension, and post-extension states. Comments state that logredo can reconstruct pre-extension bmap file state by ignoring bmap growth outside the prior `s_size` boundary.

## Important Dependencies

This path depends on bmap/dmap functions, imap growth, log manager operations, special inode read/write helpers, synchronous buffer writes, and xtree append support for bmap file growth.

## Notes

The function is growth-only and assumes no shrink. It updates the direct inode size after quiescing to match the block device. Error paths call `jfs_error()` after quiesce and always resume transactions before returning.
