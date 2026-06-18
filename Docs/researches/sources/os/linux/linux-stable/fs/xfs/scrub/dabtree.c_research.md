# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/dabtree.c

## Role

Generic scrub walker for XFS directory/attribute btrees. It validates DA tree shape, hashes, block pointers, sibling links, owners, headers, and dispatches leaf records to caller-specific validators.

## Key Functions

- `xchk_da_btree()` walks a directory or attribute btree from its expected root and calls a leaf record callback.
- `xchk_da_btree_block()` loads and interprets DA node, attr leaf, dir leafn, and dir leaf1 blocks.
- `xchk_da_btree_hash()` verifies hash ordering and parent hash bounds.
- `xchk_da_btree_ptr_ok()` enforces expected DA block ranges.
- `xchk_da_btree_block_check_sibling()` and `xchk_da_btree_block_check_siblings()` validate forward/back sibling links through alternate DA paths.
- `xchk_da_btree_*_verify()` multiplex buffer verification so directory leaf1 blocks can be handled as a degenerate DA tree leaf.
- `xchk_da_process_error()`, `xchk_da_set_corrupt()`, and `xchk_da_set_preen()` provide DA-specific scrub flag handling.

## Research Notes

Directory data fork DA trees are constrained to the leaf/free address range, while attr fork DA trees are unconstrained. The walker normalizes v2/v3 block magic values and detects stale padding fields on CRC filesystems.
