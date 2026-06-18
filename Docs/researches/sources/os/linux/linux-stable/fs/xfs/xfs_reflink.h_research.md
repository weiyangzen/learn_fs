# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_reflink.h

## Purpose
Declares reflink/CoW public helpers used by XFS write, remap, truncate, recovery, and allocation paths.

## Main API
Exports shared extent trimming, CoW allocation/conversion/cancellation/completion, atomic CoW completion, CoW recovery, remap prep/remap/update helpers, reflink flag scanning/clearing, unshare, realtime extent-size support checking, and maximum software atomic CoW sizing.

## Key Inline
`xfs_can_free_cowblocks` checks page-cache dirty/writeback tags and direct-I/O count to decide whether it is safe to free CoW fork blocks. This prevents freeing staging extents while dirty cache or in-flight I/O could still target them.

## Integration
The header forms the public boundary between reflink internals and bmap/iomap/writeback/remap/truncate code.
