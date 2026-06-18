# File Research: sources/os/linux/linux/fs/ntfs/runlist.c

Implements NTFS runlist allocation, merging, mapping-pairs compression/decompression, truncation, sparse/compressed-size checks, and range transforms.

Memory and primitive helpers:
- `ntfs_rl_realloc()` reallocates runlist arrays with `kvzalloc()` and preserves existing entries.
- `ntfs_rl_realloc_nofail()` provides no-fail growth for marker repair paths.
- `ntfs_rl_mm()` and `ntfs_rl_mc()` wrap runlist `memmove()`/`memcpy()`.
- `ntfs_are_rl_mergeable()` and `__ntfs_rl_merge()` detect/perform adjacent run merging for physical runs, holes, delayed allocation, and unmapped regions.

Runlist merge:
- `ntfs_runlists_merge()` merges a decompressed or newly allocated source runlist into an existing destination runlist.
- Supports insertion at hole start, split hole insertion, append at hole end, whole-hole replacement, and appending at end.
- Preserves/creates `LCN_RL_NOT_MAPPED` and `LCN_ENOENT` markers for partially mapped attributes and future extents.
- Frees the source runlist on successful merge.

Mapping-pairs decode:
- `ntfs_mapping_pairs_decompress()` parses NTFS mapping pairs into runlist elements.
- Validates `lowest_vcn`, mapping-pairs offset, length entries, VCN overflow, invalid negative LCNs, invalid zero-sized non-hole runs, and `highest_vcn`.
- Represents sparse runs as `LCN_HOLE`.
- Adds unmapped regions when more extents follow.
- Merges into an old runlist if provided.

Mapping-pairs encode:
- `ntfs_get_size_for_mapping_pairs()` computes required encoded size for a runlist range, including sparse-run rules for NTFS 3+.
- `ntfs_write_significant_bytes()` writes minimal signed little-endian byte sequences.
- `ntfs_mapping_pairs_build()` encodes runlists into mapping pairs, supports partial success with `stop_vcn`/`stop_rl`, counts delayed-allocation clusters, and rejects unmapped/corrupt runs.

Lookup and truncation:
- `ntfs_rl_vcn_to_lcn()` maps VCN to LCN or special negative status.
- `ntfs_rl_find_vcn_nolock()` returns the element containing a VCN if mapped or valid terminator.
- `ntfs_rl_truncate_nolock()` shrinks, expands with holes, or preserves terminator state for a locked runlist.

Sparse/compressed helpers:
- `ntfs_rl_sparse()` reports whether the runlist contains holes or delayed allocation.
- `ntfs_rl_get_compressed_size()` sums physically allocated run lengths and converts to bytes.

Range transforms:
- `ntfs_rl_insert_range()` inserts a source range into a destination runlist, splitting and merging contiguous runs.
- `ntfs_rl_punch_hole()` extracts a physical range into `punch_rl`, replaces it with a hole, handles split endpoints, and merges neighboring holes.
- `ntfs_rl_collapse_range()` extracts and removes a range, shifts following VCNs down, and merges adjacent compatible runs.

Important invariants:
- Runlists are VCN-ordered and terminated with a zero-length element, usually `LCN_ENOENT`.
- Special negative LCN values carry semantic states: hole, delayed allocation, not mapped, not found, memory/I/O/invalid errors.
- Callers must hold runlist locks where noted; most functions do not lock internally.
