# File Research: sources/local-fs/ntfs-3g/ntfsprogs/playlog.c

## Purpose
NTFS transaction-log replay helper that can redo or undo a linked list of parsed logged actions. It applies NTFS `$LogFile` action records to raw clusters, MFT records, or INDX records.

## Public Entry Points
- `play_redos(ntfs_volume *vol, const struct ACTION_RECORD *firstaction)`: applies redo actions from earliest to latest when `ACTION_TO_REDO` is set.
- `play_undos(ntfs_volume *vol, const struct ACTION_RECORD *lastaction)`: applies undo actions from latest to earliest.
- `show_redos()`: debug display of redo action kinds executed.
- `freeclusterentry()`: frees the in-memory cluster-store tree used in no-action mode.

## Global Context
Uses globals and helpers from `ntfsrecover.h`/related recovery code, including:
- `clusterbits`, `clustersz`, `mftrecbits`, `mftrecsz`.
- `latest_lsn`, `restart_lsn`.
- `opts`, `optn`, `optv`, `optc`.
- `redos_met`, `redocount`, `undocount`.
- `within_lcn_range()`, `exception()`, `actionname()`, attribute-table helpers.

## In-Memory Cluster Store
- `struct STORE` is a binary tree keyed by LCN.
- In `-n` no-action mode, writes are stored in memory so later reads can observe prior simulated writes.
- `read_raw()` checks this store before reading the block device.
- `write_raw()` writes either to the store or to the device.

## Record I/O
- `read_protected()` reads clusters for protected MFT/INDX records and applies MST post-read fixups.
- If a protected record is smaller than a cluster, it extracts the record portion based on `cluster_index`.
- `write_protected()`:
  - Validates and logs MFT/INDX records.
  - Runs rough sanity checks.
  - Sets the record LSN during redo paths.
  - Applies MST pre-write fixups.
  - Merges sub-cluster records into a full cluster when needed.
  - Mirrors early MFT records to `$MFTMirr` when within mirror coverage.

## Sanity Checks
- `valid_type()` enumerates known NTFS attribute types.
- `sanity_mft()` checks attribute ordering, instance bounds, duplicate instances, index-root embedded entries, and record lengths.
- `sanity_indx_list()` and `sanity_indx()` validate index entry alignment, end markers, and INDX allocated/index lengths.
- These checks are rough consistency guards, not full fsck-style validation.

## Generic Mutation Helpers
- Resident attribute mutation: `change_resident()`, `change_resident_expect()`, `add_resident()`, `expand_resident()`, `insert_resident()`, `remove_resident()`, `delete_resident()`, `shrink_resident()`.
- Index mutation: `change_index_value()`, `update_index()`, add/delete root/allocation index variants.
- Mapping-pair mutation: `redo_update_mapping()` and `undo_update_mapping()` update mapping pairs, resize the attribute/MFT record, and recompute `highest_vcn`.
- Bitmap mutation: redo/undo force bits set or clear bits in nonresident bitmaps.
- File create/delete mutation toggles `MFT_RECORD_IN_USE` and copies logged record data.

## Redo Dispatch
- `play_one_redo()` classifies action records as acting on MFT, INDX, raw data, or none.
- MFT/INDX records are read and compared by LSN to avoid reapplying already-executed actions, with exception overrides.
- `distribute_redos()` maps NTFS log operations to redo handlers, including:
  - index entry add/delete/update,
  - root index add/delete/update,
  - create/delete attributes,
  - create/deallocate file record segment,
  - bitmap bit changes,
  - nonresident value updates,
  - resident value updates,
  - mapping-pair updates,
  - Win10 action 37,
  - write-end operations.

## Undo Dispatch
- `play_one_undo()` similarly classifies target record type.
- For structured records, it generally only undoes actions whose target record is not older than the action LSN.
- If an INDX block cannot be read while undoing deletion of an index allocation entry, it may synthesize an empty INDX block with `create_indx()`.
- `distribute_undos()` maps the same operation families to inverse handlers.

## Important Limitations
- Several paths are intentionally incomplete:
  - `delete_non_resident()` prints not implemented and fails.
  - `add_non_resident()` prints not implemented but returns success.
- Several comments warn that synthetic recreation is useful for “turning the clock backward” but cannot work generally for real synchronization.
- `insert_index_allocation()` and `create_indx()` are explicitly unsupported when `opts` indicates normal sync/recovery use.
- `rebuildname()` currently allocates and fills an attribute but frees it without attaching it; comments suggest it should be dropped.
- Some undo paths ignore missing undo data or force success for attribute-open bookkeeping.
- Many operations rely on logged offsets and lengths being sane and aligned; guards exist, but this is still low-level metadata surgery.

## Research Relevance
This file is a dense map of how NTFS-3G interprets Windows log operations into concrete MFT, INDX, bitmap, and raw-data mutations. It is especially useful for studying NTFS recovery semantics, action idempotence, LSN-based replay decisions, and the practical gaps between full redo recovery and best-effort undo/time-reversal.
