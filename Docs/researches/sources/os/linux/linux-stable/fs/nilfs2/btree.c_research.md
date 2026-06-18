# File Research: sources/os/linux/linux-stable/fs/nilfs2/btree.c

## Summary
Implements the NILFS B-tree block map. It maps file or metadata logical keys to data or node pointers, supports insertion/deletion/rebalancing, handles direct-to-B-tree conversion, propagates dirty blocks for log writing, assigns physical blocks, and provides GC-specific operations.

## Main Responsibilities
- Manages B-tree node layout, binary search, validation, movement, insertion, and deletion.
- Performs lookup, contiguous lookup, seek, last-key lookup, and data gathering.
- Implements B-tree insertion with carry-left, carry-right, split, and grow operations.
- Implements deletion with borrow-left, borrow-right, concat-left, concat-right, and shrink operations.
- Converts a direct map into a B-tree when direct pointers overflow.
- Propagates dirty data and node buffers through DAT and parent pointers.
- Orders dirty node buffers by B-tree level for segment construction.
- Assigns physical block numbers and emits block information records.
- Provides alternate operations for garbage-collection inodes.

## Important Behavior
Tree paths are allocated from `nilfs_btree_path_cache` as arrays indexed by B-tree level. The root node is embedded in the inode bmap storage, while non-root nodes live in the associated B-tree node cache inode.

Node validation rejects impossible level, flag, or child counts. Non-root node buffers are checked once with `buffer_nilfs_checked`; failures clear uptodate state and return corruption-style errors to the bmap layer.

Lookup descends from the embedded root through cached node blocks, optionally readahead-reading sibling leaf nodes. Contiguous lookup translates virtual pointers through DAT when needed and returns the physical run length only while keys and physical blocks remain consecutive.

Insert preparation first allocates the new data pointer, then walks upward deciding whether a node can accept the entry, can redistribute with a sibling, must split, or must grow the root. Commit finalizes pointer allocation, invokes the saved per-level operation, marks the bmap dirty, and updates inode block counts.

Delete preparation reserves pointer end operations for removed data or node blocks, then selects simple deletion, sibling borrow, sibling concat, or root shrink. Commit ends the pointers, performs the structural edits, marks the bmap dirty, and decrements inode block counts.

Virtual-pointer propagation uses DAT update transactions. If a dirty node buffer is not volatile, the code allocates a new virtual pointer, prepares a node-cache key change, commits DAT update, moves the node cache key, marks the buffer volatile, and updates the parent pointer. Physical-pointer propagation only dirties ancestors.

Dirty node lookup scans the associated node cache for dirty folios and sorts buffers by level and first key before segment construction. Assignment paths update DAT for virtual pointers or parent node pointers for physical pointers and fill the appropriate on-disk `nilfs_binfo`.

## Risks
The file uses several internal status conventions and multi-step prepare/commit/abort protocols. B-tree node-cache key movement, DAT virtual pointer lifetime updates, and parent pointer replacement must remain synchronized. Corruption is surfaced as `-EINVAL` or `-EIO` depending on whether the bmap layer should treat the metadata as broken.
