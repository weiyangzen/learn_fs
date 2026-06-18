# File Research: sources/local-fs/ocfs2-tools/libocfs2/dirblock.c

Purpose: directory block, directory trailer, and indexed-directory block I/O helpers for libocfs2.

Key responsibilities:
- Computes and locates `struct ocfs2_dir_block_trailer` at the end of a filesystem block.
- Decides when a directory block has a trailer based on inline-data state, indexed-dir support, and metadata ECC support.
- Initializes directory trailers with signature, compatible record length, block number, and parent dinode.
- Swaps directory entries, directory trailers, dx root blocks, dx entry lists, and dx leaf blocks for big-endian hosts.
- Reads and writes directory data blocks with optional trailer validation and metadata ECC.
- Reads and writes indexed directory root and leaf blocks with signature and ECC validation.

Important APIs:
- `ocfs2_dir_trailer_blk_off()`, `ocfs2_dir_trailer_from_block()`
- `ocfs2_dir_has_trailer()`, `ocfs2_supports_dir_trailer()`, `ocfs2_skip_dir_trailer()`, `ocfs2_is_dir_trailer()`
- `ocfs2_init_dir_trailer()`
- `ocfs2_read_dir_block()`, `ocfs2_write_dir_block()`
- `ocfs2_read_dx_root()`, `ocfs2_write_dx_root()`
- `ocfs2_read_dx_leaf()`, `ocfs2_write_dx_leaf()`

Core invariants:
- Inline-data directories do not use external block trailers.
- Indexed directories always require trailers when the indexed-dir feature is active.
- Directory-entry swapping walks `rec_len` records and flags corrupt blocks when record lengths are too small, unaligned, or cannot hold the name length.
- Dx root and dx leaf writes use a temporary block copy so caller-owned CPU-order buffers are not modified.

Dependencies:
- Uses `ocfs2_read_blocks()`, `io_write_block()`, `ocfs2_malloc_block()`, `ocfs2_validate_meta_ecc()`, and `ocfs2_compute_meta_ecc()`.
- Delegates extent-list swapping for non-inline dx roots to `ocfs2_swap_extent_list_to_cpu()` / `from_cpu()`.

Notable behavior:
- `ocfs2_write_dir_block()` always computes ECC against the trailer location, even if the filesystem does not use trailers; `ocfs2_compute_meta_ecc()` is expected to no-op when unsupported.
- Block number range and read-write checks are explicit for dx root/leaf writes, but plain directory block writes rely on lower-level I/O validation.
