# File Research: sources/os/linux/linux-stable/fs/nilfs2/btree.h

## Summary
Defines NILFS B-tree constants, path state, and the public B-tree bmap interfaces.

## Main Contents
- `struct nilfs_btree_path`, one entry per tree level during operations.
- Root and non-root node capacity macros.
- Key range constants.
- B-tree initialization, conversion, GC initialization, and node validation declarations.

## Important Details
`nilfs_btree_path` stores current and sibling buffers, child indexes, old/new pointer requests, node cache change-key context, and the rebalance operation selected during prepare.

## Risks
Capacity macros depend on on-disk node layout and block size. Path entries carry both buffer references and transactional pointer requests, so callers must release paths through the B-tree helpers rather than manually.
