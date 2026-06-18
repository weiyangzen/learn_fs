# File Research: sources/os/linux/linux-stable/fs/nilfs2/direct.c

## Summary
Implements the NILFS direct block pointer bmap, used for small files before conversion to a B-tree.

## Main Responsibilities
- Stores and retrieves direct pointers from inode bmap data.
- Looks up single and contiguous logical blocks.
- Inserts and deletes direct block mappings.
- Seeks and gathers direct keys.
- Converts back from B-tree data into direct layout after deletion.
- Propagates dirty blocks through DAT when using virtual block numbers.
- Assigns physical block numbers during segment construction.

## Important Behavior
Direct pointers are stored as little-endian 64-bit entries following a direct-node header. Keys are limited to `0..NILFS_DIRECT_KEY_MAX`; invalid entries use `NILFS_BMAP_INVALID_PTR`.

Lookup-contiguous translates virtual pointers through DAT when the bmap uses virtual block numbers, then only extends the run while physical blocks are consecutive. DAT `-ENOENT` is converted to `-EINVAL` to signal metadata corruption.

Insert prepares a pointer allocation, treats the incoming pointer argument as a `struct buffer_head *`, marks that buffer volatile, commits the allocated pointer, stores it, marks the bmap dirty, records the target virtual pointer for sequential allocation, and increments block counts.

Delete prepares and commits pointer end, clears the direct slot, and decrements block counts. `nilfs_direct_delete_and_convert()` deletes one key, clears old bmap resources, rebuilds the direct pointer array from supplied key/pointer arrays, and reinitializes direct operations.

Propagation updates DAT if the data buffer is no longer volatile; otherwise it only marks the existing DAT entry dirty. Assignment writes either virtual block info or direct physical block info into the segment binfo record.

## Risks
The insert API receives a pointer encoded as an integer and assumes it is a buffer head. Direct mapping correctness depends on direct key range checks and on DAT update operations staying synchronized with buffer volatility.
