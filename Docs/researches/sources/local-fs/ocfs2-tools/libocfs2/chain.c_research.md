# File Research: sources/local-fs/ocfs2-tools/libocfs2/chain.c

Handles allocation-chain traversal and group descriptor I/O.

Group descriptor read/write validates block bounds, performs metadata ECC validation/computation, checks `OCFS2_GROUP_DESC_SIGNATURE`, and swaps fields for non-little-endian hosts. Discontiguous group descriptors also swap their embedded extent lists.

`ocfs2_chain_iterate()` reads a chain allocator inode, verifies it is valid and chain-backed, then walks each chain record and linked group descriptor list. It checks each descriptor’s `bg_blkno` and `bg_chain` against the traversal position and reports corruption through callback flags.

`ocfs2_get_block_from_group()` maps a bitmap bit offset to a block number for contiguous and discontiguous groups. `ocfs2_cache_chain_allocator_blocks()` primes the I/O cache by vector-reading chain heads and successor group descriptors while the estimated group-size footprint fits the channel cache.

Debug mode walks and prints chain group free/total counts.
