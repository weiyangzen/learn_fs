# File Research: sources/os/linux/linux-stable/fs/f2fs/extent_cache.c

`extent_cache.c` implements F2FS in-memory extent caching. It supports two extent types: read extents mapping file offsets to physical blocks, and block-age extents used to estimate data temperature from allocation age. Per-inode extent trees are stored in radix trees under each `extent_tree_info`, while each inode tree uses an rb-tree plus a cached node and, for read extents, a separately tracked largest extent.

`sanity_check_extent_cache()` validates the on-disk inode read extent against block-address validity and device-aliasing constraints. Device alias extents must match a non-meta device range and must not alias a zoned block device.

Extent-tree eligibility is controlled by mount options, inode type, `FI_NO_EXTENT`, compressed/cold-file restrictions, readonly compression handling, device aliasing, and whether the mount has registered shrinker/list state. Initialization either grabs/creates an extent tree or drops invalid on-disk largest-extent metadata and marks `FI_NO_EXTENT`.

Lookup first checks the read cache’s largest extent, then the per-inode cached node, then the rb-tree. Hits update statistics, move nodes to the global LRU list, and refresh the cached node. Insert/update paths use neighbor-aware rb-tree lookup so new ranges can merge with adjacent extents or split/delete overlapping extents.

`__update_extent_tree_range()` is the central invalidation/update routine. It rejects zero-length updates, drops overlapping largest extents, finds the first overlapping node, splits surviving left/right portions when large enough, removes fully invalidated nodes, then inserts or merges the new read or block-age extent. Small fragmented read-cache updates can disable future read extents for the inode by setting `FI_NO_EXTENT`.

Compressed read extent updates store logical length and compressed length so compressed clusters can be cached without being merged incorrectly with incompatible extents. Block-age updates compute a weighted age from `allocated_data_blocks`, prior age, and last allocation count, with invalidation support through `F2FS_EXTENT_AGE_INVALID`.

Shrinking first reclaims zombie extent trees left by evicted but still-linked inodes, then reclaims LRU extent nodes using trylocks to avoid blocking. Destroy/drop paths either free all nodes immediately, move live trees to the zombie list, remove radix-tree entries, or clear read largest-extent state and mark the inode dirty when persistent inode extent metadata changed.

Public operations include read extent lookup/block lookup/update/range update/shrink, age extent lookup/update/range invalidation/shrink, per-inode node/tree destroy, per-inode drop, per-mount extent-cache info initialization, and global slab-cache create/destroy. The file’s key invariants are rb-tree non-overlap, correct global LRU membership, radix-tree lifetime under `extent_tree_lock`, per-tree updates under `et->lock`, and global node-list changes under `extent_lock`.
