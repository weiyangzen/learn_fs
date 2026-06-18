# File Research: sources/os/linux/linux/fs/verity/pagecache.c

## Purpose
Provides generic pagecache helpers for filesystems storing fs-verity Merkle tree pages in their inode mapping, plus a helper to fill zero-hash ranges.

## Main Functions
- `generic_read_merkle_tree_page()`: reads a mapping folio and returns the requested page.
- `generic_readahead_merkle_tree()`: initiates pagecache readahead for Merkle tree pages if absent or not uptodate.
- `fsverity_fill_zerohash()`: fills a folio range with repeated zero-data-block digests.

## Important Design Points
- Filesystem callers must translate Merkle-tree-relative indexes to actual pagecache indexes before using the generic helpers.
- Readahead helper asserts the mapping invalidate lock is held.
- `fsverity_fill_zerohash()` requires offset and length alignment to digest size.

## Cross-File Relationships
- Used by filesystem-specific fs-verity operations.
- Zero digest comes from `fsverity_info.tree_params.zero_digest`.

## Risks / Review Notes
- Index translation is the caller’s responsibility; wrong offsets would verify against wrong tree data.
- Readahead uses unbounded pagecache readahead and must be called with appropriate locking.
