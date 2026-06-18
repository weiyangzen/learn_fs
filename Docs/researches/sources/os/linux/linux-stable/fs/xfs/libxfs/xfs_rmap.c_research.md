# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_rmap.c

## Scope

Implements XFS reverse mapping record operations for per-AG and realtime reverse-map btrees. It handles map/unmap/convert operations, shared-reflink variants, owner validation, deferred intent replay, live update hooks, raw insertion, range queries, owner-count checks, and slab cache lifecycle.

## APIs And Entry Points

- Primitive operations: `xfs_rmap_lookup_le`, `xfs_rmap_lookup_eq`, `xfs_rmap_insert`, `xfs_rmap_get_rec`, `xfs_rmap_btrec_to_irec`, `xfs_rmap_check_irec`, `xfs_rtrmap_check_irec`.
- Public map/free wrappers: `xfs_rmap_alloc`, `xfs_rmap_free`.
- Deferred replay: `__xfs_rmap_finish_intent`, `xfs_rmap_finish_one`.
- Intent producers: `xfs_rmap_map_extent`, `xfs_rmap_unmap_extent`, `xfs_rmap_convert_extent`, `xfs_rmap_alloc_extent`, `xfs_rmap_free_extent`.
- Query helpers: `xfs_rmap_lookup_le_range`, `xfs_rmap_query_range`, `xfs_rmap_query_all`, `xfs_rmap_has_records`, `xfs_rmap_count_owners`, `xfs_rmap_has_other_keys`.
- Raw and comparison helpers: `xfs_rmap_map_raw`, `xfs_rmap_compare`.
- Live hook APIs under `CONFIG_XFS_LIVE_HOOKS`: enable/disable/add/delete/setup.
- Slab lifecycle: `xfs_rmap_intent_init_cache`, `xfs_rmap_intent_destroy_cache`.

## Data Model

- Reverse-map records are keyed by physical group block, owner, and packed offset/flags.
- File data rmaps can overlap on reflink filesystems because multiple owners can map the same physical blocks.
- Metadata rmaps and bmbt/attr/non-inode owners are non-shareable and use simpler non-overlapping map/unmap logic.
- Offset packing stores attr-fork, bmbt-block, and unwritten flags in high offset bits; unwritten status is treated as a record attribute for btree key purposes.

## Control Flow

- Validation:
  - AG records validate extent range, owner class, flags, bmbt offset rules, unwritten restrictions, and file offset ranges.
  - Realtime records reject bmbt/attr flags, validate RT metadata owners separately, and require valid rtgroup extents for inode-owned records.
- Mapping:
  - `xfs_rmap_map` handles non-overlapping insertion and merges with compatible left/right neighbors.
  - `xfs_rmap_map_shared` uses delete/insert style updates because adjacent records in an overlapping btree can belong to other owners.
- Unmapping:
  - `xfs_rmap_unmap` removes or trims exact, left, right, or middle portions of a non-overlapping record. It has special handling for growfs null-owner checks and unknown-owner EFI recovery.
  - `xfs_rmap_unmap_shared` performs equivalent operations for shareable file data using owner/offset-aware range lookup and delete/insert where key fields change.
- Conversion:
  - `xfs_rmap_convert` toggles unwritten state for non-overlapping extents and handles eight main combinations of left/right filling and contiguous merge state.
  - `xfs_rmap_convert_shared` performs the same logical transformation for overlapping reflink data records.
- Deferred replay:
  - `xfs_rmap_finish_one` reuses a cursor when intents target the same group, initializes AG or realtime cursors as needed, reconstructs owner info from intent state, calls `__xfs_rmap_finish_intent`, then emits live hooks.
- Owner analysis:
  - `xfs_rmap_count_owners` trims queried records to the comparison range and counts owner/non-owner/conflicting non-owner matches.
  - `xfs_rmap_has_other_keys` stops early when any non-owner match is found.

## Dependencies

- Uses generic btree APIs, rmap btree cursors, realtime rmap cursors, transactions, bmap extent records, owner-info helpers, perag/rtgroup group state, filesystem feature flags, tracepoints, health marking, error tags, and deferred rmap log item infrastructure.
- Live hooks depend on XFS hook infrastructure and static jump-label switches.

## Invariants And Risks

- Shared reflink data paths must use overlapping-aware lookup; using the simple non-overlapping path can update the wrong owner record.
- Owner, offset, fork, bmbt, and unwritten flags are part of corruption detection, not advisory metadata.
- Unknown-owner free exists for log recovery and deliberately weakens owner checks; other callers should not use it casually.
- Deferred cursor reuse assumes operations are sorted by group and that cursor group mismatches are detected before replay.
- Realtime and AG validation rules differ; record checkers must be selected from cursor type.
