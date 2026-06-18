# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_da_btree.c

## Scope

This file implements the shared XFS directory/attribute Btree machinery: DA state allocation, v2/v3 node header conversion and verification, node buffer reads, tree split/join, node rebalance/unbalance, path shifting, hash maintenance, name hashing/comparison, logical DA block allocation/removal, buffer mapping, and readahead.

## Main Interfaces

- State lifecycle: `xfs_da_state_alloc()`, `xfs_da_state_free()`, `xfs_da_state_reset()`.
- Header and verifier helpers: `xfs_da3_node_hdr_from_disk()`, `xfs_da3_node_hdr_to_disk()`, `xfs_da3_blkinfo_verify()`, `xfs_da3_node_header_check()`, `xfs_da3_header_check()`.
- Buffer operations: `xfs_da3_node_read()`, `xfs_da3_node_read_mapped()`, `xfs_da_get_buf()`, `xfs_da_read_buf()`, `xfs_da_reada_buf()`, `xfs_da_buf_copy()`.
- Btree growth: `xfs_da3_node_create()`, `xfs_da3_split()`, `xfs_da3_blk_link()`.
- Btree shrink: `xfs_da3_join()`, `xfs_da3_fixhashpath()`, `xfs_attr3_node_entry_remove()`, `xfs_da_shrink_inode()`.
- Search and traversal: `xfs_da3_node_lookup_int()`, `xfs_da3_path_shift()`.
- Utility: `xfs_da_hashname()`, `xfs_da_compname()`, `xfs_da_grow_inode()`, `xfs_da_grow_inode_int()`.

## Control Flow And Behavior

DA nodes are common infrastructure for both directory leaf/node format and attribute leaf/node format. The code normalizes v2 and v3 on-disk node headers into `xfs_da3_icnode_hdr` so most tree algorithms can ignore CRC-era layout differences. Read verifiers inspect magic, CRC metadata, UUID, block address, LSN validity, level, count, and ownership checks; leaf blocks discovered during ambiguous node reads have their buffer ops switched to the attr or dir leaf verifier.

Insertion starts at the leaf and walks upward through `xfs_da3_split()`. Leaf splits are delegated to attr or dir leaf code; internal node splits allocate a new DA block, rebalance entries, link the new block into the same-level sibling chain, insert child pointers, and propagate final hash values upward. Root splits copy the old root to a new block and create a fresh root with two child pointers.

Removal and shrink run through `xfs_da3_join()`. Leaf or node blocks that become too small are coalesced with a sibling when possible; empty blocks are unlinked and unmapped. If the root has a single remaining child, `xfs_da3_root_join()` copies that child back to block zero and frees the old child block.

Search descends from the root block, binary-searching internal node hash values while accounting for duplicate hashes. At the leaf level it delegates to directory or attribute lookup code. If the leaf’s last hash equals the search hash and lookup fails, it shifts to the next leaf to continue duplicate-hash search.

Logical DA block allocation uses bmap helpers to find unused file offsets and allocate contiguous filesystem blocks when possible. Directory block removal has a fallback for `-ENOSPC`: `xfs_da3_swap_lastblock()` moves the last DA block into the block being removed so the final mapping can be punched without needing a bmap split.

## State And Data Structures

- Uses `xfs_da_state`, `xfs_da_state_path`, and `xfs_da_state_blk` to track active root-to-leaf paths plus alternate paths for sibling joins.
- Uses `xfs_da_geometry` from the mount to interpret directory vs attribute block size, node capacity, leaf/free/data regions, and fork extent limits.
- Internal node entries store a descendant’s final hash and logical block number.
- Same-level blocks use `xfs_da_blkinfo` forward/back links; CRC filesystems embed this in `xfs_da3_blkinfo`.

## Dependencies

Depends on attr leaf helpers, dir leaf helpers, bmap allocation/unmapping, transaction buffer logging, buffer verifiers, metadata health marking, XFS error injection, and mount geometry initialized by directory setup.

## Risks And Invariants

- Internal node hash values must always equal the last hash in each child subtree; `xfs_da3_fixhashpath()` repairs this after split/join edits.
- Duplicate hashes require scanning sibling leaves; lookup changes must preserve path shifting behavior.
- DA block link/unlink must update both neighbors and validate owners before trusting sibling blocks.
- `xfs_da3_swap_lastblock()` is delicate because it updates sibling links and parent pointers after moving a block’s contents.
- v2/v3 layout abstraction depends on magic checks and correct buffer ops switching for node-vs-leaf ambiguity.
