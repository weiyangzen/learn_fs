# File Research: sources/os/linux/linux/fs/xfs/xfs_reflink.h

## Role

Public internal header for XFS reflink/CoW helpers.

## Main Contents

- `xfs_can_free_cowblocks`: checks whether it is safe to discard CoW fork blocks by ensuring no dirty pages, writeback, or direct IO are active.
- Declarations for shared extent trimming, CoW allocation/conversion/cancelation, CoW completion, atomic CoW, CoW recovery, remap preparation/blocks/update, reflink flag clearing, unshare, realtime extent-size support, and maximum atomic CoW sizing.

## Important Contract

Callers must respect IO/pagecache safety before freeing CoW fork blocks. Many declarations assume inode locks or transaction joins are managed by the caller or described in the implementation comments.

## Dependencies

References XFS inodes, bmap records, transactions, files, offsets, and mount-level realtime/reflink capabilities.
