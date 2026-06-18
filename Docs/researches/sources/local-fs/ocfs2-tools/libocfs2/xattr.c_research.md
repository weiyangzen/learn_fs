# File Research: sources/local-fs/ocfs2-tools/libocfs2/xattr.c

Implements extended attribute hashing, byte-order conversion, block/bucket read-write helpers, and xattr iteration for OCFS2.

Key responsibilities:
- Hashes volume UUID and xattr names.
- Computes bucket/block layout values.
- Swaps xattr headers, entries, block headers, value roots, tree roots, and nested extent lists.
- Reads and writes xattr blocks with metadata ECC validation/computation.
- Reads and writes xattr buckets, including bucket ECC.
- Locates indexed xattr records by name hash.
- Iterates inline inode xattrs, external xattr blocks, and indexed xattr buckets.

Important functions:
- `ocfs2_xattr_uuid_hash()` / `ocfs2_xattr_name_hash()`.
- `ocfs2_swap_xattrs_to_cpu()` / `ocfs2_swap_xattrs_from_cpu()`.
- `ocfs2_read_xattr_block()` / `ocfs2_write_xattr_block()`.
- `ocfs2_read_xattr_bucket()` / `ocfs2_write_xattr_bucket()`.
- `ocfs2_xattr_get_rec()`: finds the extent record covering a name hash in an indexed xattr tree.
- `ocfs2_xattr_iterate()`: public iterator over all xattr storage locations.

Dependencies:
- Byteorder helpers, metadata ECC helpers, extent-list swap and search APIs.
- `ocfs2_tree_find_leaf`, `ocfs2_read_blocks`, `io_write_block`.

Research notes:
- Xattr swap handling is complex because headers may live in inode tails, xattr blocks, or 4K buckets independent of filesystem block size.
- The implementation uses a fake `ocfs2_filesys` with `fs_blocksize = objsize` for swap-barrier checks.
- Iteration stops on `OCFS2_XATTR_ABORT` or `OCFS2_XATTR_ERROR`; callers that mutate xattrs must restart.
