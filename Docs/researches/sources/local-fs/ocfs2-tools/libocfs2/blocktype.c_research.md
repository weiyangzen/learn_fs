# File Research: sources/local-fs/ocfs2-tools/libocfs2/blocktype.c

Detects OCFS2 metadata block types by comparing known signatures at structure-specific offsets.

The signature table recognizes inodes, superblocks, extent blocks, group descriptors, directory trailer blocks, xattr blocks, refcount blocks, DX roots, and DX leaves. `ocfs2_detect_block()` returns an `ocfs2_block_type` or `OCFS2_BLOCK_UNKNOWN`.

`ocfs2_swap_block_to_cpu()` and `ocfs2_swap_block_from_cpu()` dispatch to the correct per-structure byte-swap routine based on detected type. Unknown blocks are intentionally ignored, so callers that need strict validation must detect unknown types themselves.
