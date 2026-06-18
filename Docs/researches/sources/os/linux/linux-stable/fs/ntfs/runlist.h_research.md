# File Research: sources/os/linux/linux-stable/fs/ntfs/runlist.h

`runlist.h` defines NTFS in-memory runlist data structures, special LCN values, initialization, and public runlist APIs.

Key definitions:
- `struct runlist_element` maps a starting VCN to an LCN and cluster length.
- `struct runlist` wraps a runlist array with an `rw_semaphore`, element count, and hint index.
- `ntfs_init_runlist()` initializes an empty runlist with no array, a ready rwsem, count zero, and hint `-1`.

Special LCN states:
- `LCN_DELALLOC = -1`
- `LCN_HOLE = -2`
- `LCN_RL_NOT_MAPPED = -3`
- `LCN_ENOENT = -4`
- `LCN_ENOMEM = -5`
- `LCN_EIO = -6`
- `LCN_EINVAL = -7`

Declared APIs:
- Merge/decompression: `ntfs_runlists_merge()`, `ntfs_mapping_pairs_decompress()`.
- Lookup/conversion: `ntfs_rl_vcn_to_lcn()`, `ntfs_rl_find_vcn_nolock()`.
- Mapping-pair sizing/building: `ntfs_get_size_for_mapping_pairs()`, `ntfs_mapping_pairs_build()`.
- Mutation: `ntfs_rl_truncate_nolock()`, `ntfs_rl_insert_range()`, `ntfs_rl_punch_hole()`, `ntfs_rl_collapse_range()`, `ntfs_rl_realloc()`.
- Inspection/accounting: `ntfs_rl_sparse()`, `ntfs_rl_get_compressed_size()`.

Design role:
- This header is the interface between NTFS attribute code and the runlist implementation.
- It standardizes negative LCN sentinel meanings used throughout the driver.
