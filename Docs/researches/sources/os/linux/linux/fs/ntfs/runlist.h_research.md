# File Research: sources/os/linux/linux/fs/ntfs/runlist.h

Public header for NTFS runlist handling.

Defines:
- `struct runlist_element` with `vcn`, `lcn`, and `length`.
- `struct runlist` with runlist pointer, read/write semaphore, element count, and hint index.
- `ntfs_init_runlist()` initializer.
- Special negative LCN/status constants: `LCN_DELALLOC`, `LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`, `LCN_ENOMEM`, `LCN_EIO`, `LCN_EINVAL`.

Exports:
- Merge/decompress/lookup helpers: `ntfs_runlists_merge()`, `ntfs_mapping_pairs_decompress()`, `ntfs_rl_vcn_to_lcn()`, `ntfs_rl_find_vcn_nolock()`.
- Mapping-pairs encode sizing/build APIs.
- Truncate, sparse, compressed-size, insert, punch-hole, collapse-range, and realloc APIs.

Role:
- Shared runlist abstraction used by attribute mapping, MFT growth, cluster allocation, writeback, and sparse/compressed data handling.
