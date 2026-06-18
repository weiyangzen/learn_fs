# File Research: sources/os/linux/linux-stable/fs/ntfs/runlist.c

`runlist.c` implements NTFS runlist manipulation and mapping-pair encode/decode logic. Runlists map virtual cluster numbers to logical cluster numbers or special negative states such as holes, delayed allocation, unmapped regions, and terminators.

Key responsibilities:
- Memory helpers `ntfs_rl_mm()`, `ntfs_rl_mc()`, `ntfs_rl_realloc()`, and internal no-fail reallocation support runlist array movement/growth.
- Merge helpers determine whether adjacent runs can combine, then append, insert, replace, or split destination runlists around source mappings.
- `ntfs_runlists_merge()` merges a decompressed or newly allocated source runlist into an existing destination runlist, preserving holes/unmapped markers and `LCN_ENOENT` terminators.
- `ntfs_mapping_pairs_decompress()` parses on-disk NTFS mapping pairs into an in-memory runlist and optionally merges it into an old runlist.
- `ntfs_rl_vcn_to_lcn()` converts a VCN to an LCN or special negative mapping state.
- `ntfs_rl_find_vcn_nolock()` locates the runlist element containing a VCN.
- `ntfs_get_size_for_mapping_pairs()` calculates the byte size needed to encode part or all of a runlist as mapping pairs.
- `ntfs_mapping_pairs_build()` encodes a runlist into mapping pairs, with partial-success support through `stop_vcn`/`stop_rl` on `-ENOSPC`.
- `ntfs_rl_truncate_nolock()` shrinks or expands a runlist to a new VCN length, adding sparse holes when expanding.
- `ntfs_rl_sparse()` checks whether a runlist contains sparse or delayed-allocation regions.
- `ntfs_rl_get_compressed_size()` sums physically allocated clusters and returns their byte size.
- `ntfs_rl_insert_range()` inserts one runlist range into another at a VCN, splitting/merging adjacent runs where possible.
- `ntfs_rl_punch_hole()` replaces a VCN range with a hole and returns the removed physical runs through `punch_rl`.
- `ntfs_rl_collapse_range()` removes a VCN range, shifts later runs left, and returns the extracted runs.

Important validation:
- Mapping-pair decompression checks `lowest_vcn` overflow, attribute bounds, missing length fields, negative lengths, VCN overflow, invalid LCNs, zero-sized non-hole runs, and `highest_vcn` consistency.
- Encoding rejects unmapped runlist elements, corrupt negative states, invalid ranges, and insufficient destination buffer size.
- Merge operations reject overlapping concrete mappings and malformed terminators.

Design details:
- Holes on NTFS 3.0+ are encoded by omitting LCN deltas.
- Older NTFS versions may encode sparse regions differently, so code preserves special handling for volume major version below 3.
- Runlist operations generally require the caller to hold the relevant runlist lock; “nolock” names mean the function does not acquire it.
- Several operations consume/free input runlist arrays on success, which is part of their ownership contract.

Dependencies:
- Uses NTFS volume geometry and error logging from `ntfs.h`.
- Uses attribute layout definitions from `attrib.h`.
- Used heavily by attribute mapping, allocation, truncation, sparse/compressed file handling, and MFT growth.
