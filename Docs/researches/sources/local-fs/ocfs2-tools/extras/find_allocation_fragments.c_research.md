# File Research: sources/local-fs/ocfs2-tools/extras/find_allocation_fragments.c

Read coverage: complete file read, 239 lines.

Purpose: scans an OCFS2 chain allocator inode and reports contiguous free-bit fragments in its group descriptors.

Behavior:
- Usage: `find_allocation_fragments <device> <allocator_inode_block>`.
- Opens the volume read-only.
- Validates that the target inode has bitmap, chain, system, and valid flags.
- Walks each chain list entry and follows linked group descriptors.
- Finds clear-bit runs in each group bitmap, prints run length, bit offset, and group block.
- Tracks the largest free extent and builds a small histogram for free runs under 200 bits.

Dependencies: `libocfs2` inode/group descriptor reads, chain-list structures, and bitmap bit-search helpers.

Risk notes:
- Read-only diagnostic.
- It trusts chain traversal except for library read validation; a corrupted loop could lead to repeated traversal depending on lower-level safeguards.
