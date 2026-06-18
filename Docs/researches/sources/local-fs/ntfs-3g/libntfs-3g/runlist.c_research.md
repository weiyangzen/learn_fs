# File Research: sources/local-fs/ntfs-3g/libntfs-3g/runlist.c

## Scope

Implements NTFS runlist handling for libntfs-3g: in-memory runlist allocation, extension, merge/splice operations, mapping-pair decompression and rebuilding, VCN-to-LCN translation, runlist-backed scatter/gather I/O, truncation, sparse detection, and compressed-size accounting.

## API And Behavior

- Low-level helpers `ntfs_rl_mm()`, `ntfs_rl_mc()`, and `ntfs_rl_realloc()` move/copy runlist elements and grow storage in 4 KiB allocation units.
- `ntfs_rl_extend()` expands an attribute runlist while preserving the caller's interior runlist pointer relative to `na->rl`.
- Merge helpers decide whether runs can combine by VCN/LCN adjacency, including special treatment for adjacent holes and not-mapped regions.
- `ntfs_rl_append()`, `ntfs_rl_insert()`, `ntfs_rl_replace()`, and `ntfs_rl_split()` implement the four runlist splice cases used when allocated runs fill holes or newly mapped extents land inside an existing runlist.
- `ntfs_runlists_merge()` wraps the main merge engine. It accepts a new source runlist, skips source not-mapped prefix entries, rejects illegal real-data overlaps, merges into holes/not-mapped regions, preserves or creates `LCN_ENOENT` terminators, and may create not-mapped gaps when source extents do not cover the whole logical range.
- `ntfs_mapping_pairs_decompress()` converts an on-disk non-resident attribute's mapping-pairs array into a runlist, handles sparse runs with `LCN_HOLE`, validates mapping-pair bounds and negative/zero run cases, compares `highest_vcn`, and adds either `LCN_ENOENT` or `LCN_RL_NOT_MAPPED` terminators depending on extent completeness.
- `ntfs_rl_vcn_to_lcn()` maps a VCN through a runlist and returns negative sentinel values for holes, not-yet-mapped regions, missing VCNs, and invalid input.
- `ntfs_rl_pread()` reads logical byte ranges through a runlist, zero-fills holes, treats unexpected negative sentinels or EOF as I/O problems, retries interrupted device reads, and returns partial byte counts when some data was read.
- `ntfs_rl_pwrite()` writes logical byte ranges through a runlist, skips sparse holes after advancing the input buffer, honors read-only volume mode by pretending writes succeeded, retries interrupted writes, and returns partial counts similarly to reads.
- Mapping-pair builders include `ntfs_get_nr_significant_bytes()`, `ntfs_get_size_for_mapping_pairs()`, `ntfs_write_significant_bytes()`, and `ntfs_mapping_pairs_build()`. They encode signed run lengths and LCN deltas compactly, omit NTFS 3.x sparse LCN fields, report `ENOSPC` with the stop run for multi-extent continuation, and reject not-mapped or corrupt runlists.
- `ntfs_rl_truncate()` trims a runlist at a VCN and installs an `LCN_ENOENT` terminator without shrinking the 4 KiB allocation, because the old shrink path is documented as broken.
- `ntfs_rl_sparse()` checks for `LCN_HOLE` runs and treats other negative run sentinels as invalid for this purpose.
- `ntfs_rl_get_compressed_size()` totals non-sparse clusters and shifts by cluster size to compute physical/compressed byte size.
- Under `NTFS_TEST`, the file includes a standalone runlist merge/decompression test harness with synthetic pure-run tests and binary mapping-pair fragment tests.

## State And Dependencies

The file operates on `runlist_element`, `ntfs_attr`, `ntfs_volume`, `ATTR_RECORD`, and device I/O callbacks. It depends on NTFS sentinel LCN values (`LCN_HOLE`, `LCN_RL_NOT_MAPPED`, `LCN_ENOENT`), volume cluster geometry, endian conversion helpers, `ntfs_malloc()`, `ntfs_pread()`, `ntfs_pwrite()`, and debug/logging helpers. It is a core dependency for non-resident attributes, attribute-list extent mapping, allocation, sparse/compressed file handling, and mapping-pair persistence.

## Risks And Invariants

Runlists must remain sorted by VCN, adjacent by logical length, and terminated by the correct sentinel. Merge operations intentionally mutate arrays only after reallocation succeeds, but there are critical paths where later terminator repair allocation is marked as impossible to recover from and deliberately crashes on failure. Mapping-pair decompression is defensive about malformed arrays, but relies on consistent attribute `length`, `lowest_vcn`, `highest_vcn`, and `allocated_size`. Mapping-pair build helpers require fully mapped runlists; passing `LCN_RL_NOT_MAPPED` is an API misuse. Sparse writes ignore supplied bytes for holes, so callers must ensure metadata and data semantics are consistent.
