# File Research: sources/os/linux/linux/fs/xfs/scrub/dabtree.c

## Role
Implements a generic scrub walker for XFS directory/attribute btrees. It validates DA tree blocks, hashes, siblings, owners, and path structure, then calls a caller-supplied callback for leaf records.

## Main Interfaces
- `xchk_da_process_error`: DA-tree equivalent of scrub operation error normalization.
- `xchk_da_set_corrupt` and `xchk_da_set_preen`: flag file-block corruption or optimization opportunities.
- `xchk_da_btree_hash`: validates monotonically increasing hashes and parent hash bounds.
- `xchk_da_btree`: top-level DA btree traversal for data or attr fork.

## Block Handling
- `xchk_da_btree_buf_ops` multiplexes buffer verification for leaf1 blocks versus generic DA node/attr leaf/dir leafn blocks.
- `xchk_da_btree_block` reads a DA block, validates pointer range, verifies buffer structure, checks CRC owner/padding fields, validates sibling pointers, interprets block magic, computes max records and last hash, and verifies parent hash expectations.
- Directory data-fork scans expect node/leaf blocks between `leafblk` and `freeblk`; attr fork scans have no DA block range limit.

## Traversal
- Skips short-format forks without extents.
- Starts at the expected root block (`lowest`) and walks using `xfs_da_state.path`.
- Leaf blocks dispatch to the supplied record scrub function.
- Node blocks validate hash ordering and descend through `before` pointers.
- Releases all tracked buffers and DA state on exit.

## Invariants and Edge Cases
- Directory leaf1 blocks are treated as a degenerate leafn form because normal DA code does not handle them directly.
- Missing directory btree root at `leafblk` is acceptable for directories but missing attr btree blocks are corrupt.
- Top-level DA blocks must not have sibling pointers; lower levels must match path-shift results.
- Node depth must remain below `XFS_DA_NODE_MAXDEPTH`.
