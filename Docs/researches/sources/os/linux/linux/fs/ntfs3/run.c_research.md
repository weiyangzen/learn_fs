# File Research: sources/os/linux/linux/fs/ntfs3/run.c

## Role

Implements NTFS runlist management. A runlist maps virtual clusters in a file to logical clusters on disk, including sparse extents. This file handles lookup, insertion, consolidation, truncation, collapse/insert range, packing into NTFS mapping-pair format, unpacking from disk, cloning, and range removal.

## Major Functions

- Internal helpers:
  - `run_lookup()`: binary-searches the run array for a VCN and returns either containing index or insertion index.
  - `run_consolidate()`: merges adjacent or overlapping compatible runs.
  - `run_packed_size()`, `run_pack_s64()`, `run_unpack_s64()`: endian-aware mapping-pair integer encoding helpers.
- Lookup and coverage:
  - `run_lookup_entry()`: returns LCN/length/index for a VCN.
  - `run_get_entry()`: returns the Nth run.
  - `run_is_mapped_full()`: checks whether a VCN range is continuously mapped.
  - `run_len()` and `run_get_max_vcn()`: summarize run coverage.
- Mutations:
  - `run_add_entry()`: inserts or overlays a run, splitting existing runs when sparse/non-sparse or LCN continuity differs.
  - `run_truncate_head()`, `run_truncate()`, `run_truncate_around()`: drop mappings before/after positions and manage memory.
  - `run_collapse_range()`: removes a logical VCN range for fallocate collapse.
  - `run_insert_range()` and `run_insert_range_da()`: inserts sparse VCN space for fallocate insert, including delayed-allocation variant.
  - `run_remove_range()`: removes a range and reports removed length.
  - `run_clone()`: copies a run tree.
- NTFS mapping-pair encoding:
  - `run_pack()`: serializes a contiguous run coverage range into NTFS packed mapping pairs.
  - `run_unpack()`: parses packed mapping pairs, checks overflows, sparse encodings, 32-bit cluster build limits, and volume bounds.
  - `run_unpack_ex()`: optionally validates unpacked allocated clusters against the volume bitmap and repairs/marks dirty when mismatches are detected.
  - `run_get_highest_vcn()`: parses mapping pairs enough to compute highest VCN, used during log replay.

## Important Invariants

- `runs_tree` is sorted by VCN and represented as a contiguous array.
- Adjacent extents are consolidated when sparse status and physical LCN continuity match.
- Sparse runs use `SPARSE_LCN`; physical runs must stay within the volume bitmap range.
- On 32-bit cluster builds, VCN/LCN ranges beyond 2^32 clusters are rejected.
- Mapping-pair unpacking treats length as unsigned and LCN delta as signed, matching NTFS disk format.
- `run_unpack()` can also be called in validation-only mode with `run == NULL`, or cluster-freeing mode with `RUN_DEALLOCATE`.

## Dependencies

- Uses kernel allocation, overflow, endian, log2 helpers, and block APIs.
- Calls bitmap/free-space helpers through `mark_as_free_ex`, `wnd_is_used`, `wnd_set_used_safe`, `wnd_zone_set`, and `ntfs_refresh_zone`.
- Relies on NTFS constants and `runs_tree` definitions from `ntfs.h` and `ntfs_fs.h`.

## Notes For Future Work

- The file explicitly notes array/memmove costs and a future extents-tree direction.
- `run_add_entry()` is complex because it overlays arbitrary ranges and may recursively add tails. It is a key area for edge-case tests.
- `run_remove_range()` splitting a middle physical run adds the tail with the original `r->lcn`; future review should verify whether that should include the removed offset when used for physical mappings.
