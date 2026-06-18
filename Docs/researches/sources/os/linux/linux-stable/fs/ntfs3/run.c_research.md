# File Research: sources/os/linux/linux-stable/fs/ntfs3/run.c

Purpose: Maintains NTFS runlists, mapping virtual cluster numbers to logical cluster numbers or sparse regions, and converts between in-memory arrays and NTFS packed mapping pairs.

Key responsibilities:
- Binary-searches run arrays with `run_lookup()` and exposes lookup through `run_lookup_entry()`.
- Adds or replaces mapped ranges with `run_add_entry()`, including overlap handling, splitting, tail reinsertion, sparse/real run separation, allocation growth, and consolidation.
- Truncates, trims, removes, collapses, and inserts ranges through `run_truncate()`, `run_truncate_head()`, `run_truncate_around()`, `run_remove_range()`, `run_collapse_range()`, `run_insert_range()`, and `run_insert_range_da()`.
- Reports mapping state with `run_get_entry()`, `run_is_mapped_full()`, `run_len()`, and `run_get_max_vcn()`.
- Packs in-memory runs into NTFS mapping-pair bytes with `run_pack()`.
- Unpacks and validates mapping-pair bytes with `run_unpack()`, optionally checking cluster allocation bitmap consistency with `run_unpack_ex()`.
- Provides `run_get_highest_vcn()` for log replay and `run_clone()` for copying run trees.

Important invariants:
- Runs are sorted by VCN and normalized by `run_consolidate()` after insertion.
- Adjacent sparse runs can merge; adjacent real runs merge only when both VCNs and LCNs are contiguous.
- `run_unpack()` rejects malformed encodings: zero lengths, oversized length/offset fields, truncated buffers, zero LCN deltas for non-sparse runs, VCN overflow, `evcn` overrun, unsupported 64-bit cluster references in 32-bit mode, and LCN ranges outside the volume bitmap.
- `RUN_DEALLOCATE` is a special mode where unpacked real clusters are freed without storing them in a run tree.
- Normal run-tree memory is capped by policy warnings around `NTFS3_RUN_MAX_BYTES`; MFT runs are allowed to exceed that warning path.

Dependencies:
- Uses allocation bitmap APIs to mark/free/check clusters.
- Uses `mark_as_free_ex()`, `ntfs_set_state()`, and MFT-zone refresh logic from other NTFS3 modules.

Risk notes:
- The array-backed run tree can require memmove-heavy operations; comments call this a bottleneck.
- `run_unpack_ex()` can repair bitmap mismatches by marking clusters used and setting the volume error state, so it has both validation and recovery side effects.
- Range insert/collapse operations assume caller-level attribute-size and on-disk persistence handling.
