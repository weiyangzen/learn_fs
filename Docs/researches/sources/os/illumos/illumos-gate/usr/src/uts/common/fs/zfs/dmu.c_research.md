# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu.c

## Role

`dmu.c` implements the main public DMU buffer and object data APIs above dbufs/dnodes: buffer holds, bonus/spill handling, prefetch, reads, writes, frees, preallocation, embedded writes, xuio support, ARC buffer assignment, ZIL `dmu_sync()`, object property setters, write policy selection, object info, byte swapping, and DMU subsystem initialization/finalization.

## Major Responsibilities

- Defines `dmu_ot[]`, the object-type table with byteswap class, metadata flag, metadata-cache flag, encryption eligibility, and human-readable names.
- Defines `dmu_ot_byteswap[]`, the byteswap function table.
- Provides public read/write APIs on `(objset, object, offset)` and dnode/dbuf variants.
- Coordinates dbuf array holds for multi-block reads/writes.
- Handles bonus and spill buffer access and mutation.
- Performs long-range frees in txg-sized chunks with dirty-free throttling.
- Supports device-removal block-pointer remap passes.
- Supports zero-copy xuio reads and loaned ARC write buffers.
- Implements `dmu_sync()` for ZIL block sync and dirty-record override handling.
- Computes zio write policy: compression, checksum, copies, dedup, nopwrite, encryption, small-block policy.
- Provides DMU object metadata queries and wait-for-sync helpers.
- Initializes and tears down DMU-adjacent subsystems.

## Key Tunables and Globals

- `zfs_nopwrite_enabled`: enables/disables nopwrite.
- `zfs_per_txg_dirty_frees_percent`: throttles long frees by dirty data budget percentage.
- `zfs_object_remap_one_indirect_delay_ticks`: testing delay for remap paths.
- `dmu_prefetch_max`: limits bytes prefetched per call.
- `zfs_redundant_metadata_most_ditto_level`: minimum indirect level for extra metadata ditto copies under `redundant_metadata=most`.
- `xuio_stats` and `xuio_ksp`: kstats for loaned read/write buffers and copy/no-copy counts.

## Important Functions

- Buffer holds:
  - `dmu_buf_hold_noread_by_dnode()`, `dmu_buf_hold_noread()`
  - `dmu_buf_hold_by_dnode()`, `dmu_buf_hold()`
  - `dmu_buf_hold_array_by_dnode()` for parallel multi-block hold/read.
  - `dmu_buf_rele_array()` releases arrays.
- Bonus/spill:
  - `dmu_bonus_hold_by_dnode()`, `dmu_bonus_hold_impl()`, `dmu_bonus_hold()`
  - `dmu_set_bonus()`, `dmu_set_bonustype()`, `dmu_get_bonustype()`
  - `dmu_spill_hold_by_dnode()`, `dmu_spill_hold_existing()`, `dmu_spill_hold_by_bonus()`, `dmu_rm_spill()`
- Prefetch:
  - `dmu_prefetch()` maps byte ranges to dbuf block IDs and calls `dbuf_prefetch()`.
- Freeing:
  - `get_next_chunk()` finds chunks for long frees by walking allocated L1 indirects backwards.
  - `dmu_free_long_range_impl()` chunks and throttles large frees.
  - `dmu_free_long_range()`, `dmu_free_long_object()`, `dmu_free_range()`.
- Reads/writes:
  - `dmu_read_impl()`, `dmu_read()`, `dmu_read_by_dnode()`
  - `dmu_write_impl()`, `dmu_write()`, `dmu_write_by_dnode()`
  - kernel-only UIO and page write variants.
- ARC buffer loan/assignment:
  - `dmu_request_arcbuf()`, `dmu_return_arcbuf()`
  - `dmu_copy_from_buf()`
  - `dmu_assign_arcbuf_by_dnode()`, `dmu_assign_arcbuf_by_dbuf()`
- ZIL sync:
  - `dmu_sync()`
  - `dmu_sync_ready()`, `dmu_sync_done()`
  - late-arrival variants for already-syncing or frozen txg cases.
- Object settings and info:
  - `dmu_object_set_nlevels()`, `dmu_object_set_blocksize()`, `dmu_object_set_maxblkid()`
  - `dmu_object_set_checksum()`, `dmu_object_set_compress()`
  - `dmu_offset_next()`, `dmu_object_wait_synced()`
  - `dmu_object_info_from_dnode()`, `dmu_object_info()`, `dmu_object_info_from_db()`
  - `dmu_object_size_from_db()`, `dmu_object_dnsize_from_db()`
- Policy/init:
  - `dmu_write_policy()`
  - `byteswap_uint{64,32,16,8}_array()`
  - `dmu_init()`, `dmu_fini()`

## Write Policy Behavior

`dmu_write_policy()` distinguishes metadata, nofill/preallocated data, and normal data. It selects compression, checksum, copies, dedup, dedup verification, nopwrite, special-small-block eligibility, and encryption. Metadata gets robust checksums and possible extra copies. Encrypted objsets disable inappropriate dedup/nopwrite combinations and reserve DVA capacity for encrypted-object requirements.

## Interactions

- Relies on `dbuf.c` for buffer hold/read/dirty/fill/assign/sync support.
- Relies on dnode routines for allocation state, object size, block hierarchy, free ranges, and object settings.
- Uses DSL pool/dataset txg sync, dirty data accounting, long-hold, and wait functions.
- Uses ZIL callbacks and LWB bookkeeping in `dmu_sync()`.
- Uses ARC for loaned buffers, raw/encrypted buffer copying, and zero-copy xuio reads.
- Uses zio properties and zio writes for sync writes.
- Uses SPA feature/property state for encryption, redundant metadata, nopwrite, dedup, and device removal.

## Notable Invariants

- Multi-block access is capped by `DMU_MAX_ACCESS`.
- Full-block writes use `dmu_buf_will_fill()`; partial writes use `dmu_buf_will_dirty()`.
- `dmu_sync()` has distinct return semantics: `EEXIST`, `ENOENT`, `EALREADY`, `EIO`, or `0`.
- Nopwrite in `dmu_sync()` is disabled if the on-disk BP might change before the target txg, such as if an older dirty record exists or the dnode has freed the block.
- Long free of an entire object resets `dn_maxblkid` on success.
- `dmu_object_info_from_dnode()` reports physical blocks from `DN_USED_BYTES()` and fill from top-level block pointers.

## Research Notes

This file is the primary consumer-facing DMU layer. It does not own low-level dbuf state, but it decides when to hold/read/dirty/fill buffers and how writes should be represented to zio. High-risk areas are `dmu_sync()` ordering, write policy changes, long-free throttling, encrypted/raw ARC buffer assignment, and multi-block hold/read error cleanup.
