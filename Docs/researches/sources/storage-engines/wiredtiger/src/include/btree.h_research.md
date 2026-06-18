# sources/storage-engines/wiredtiger/src/include/btree.h

## Purpose
This header defines the btree handle and high-level btree configuration/state. It connects logical table properties, page sizing, reconciliation settings, compression/encryption, checkpointing, eviction walk state, cache accounting, block-manager integration, disaggregated storage state, and btree flags.

## Important APIs, Types, And Functions
The file defines version constants, page/object size limits, normalized-position constants used by eviction, `WT_BTREE_TYPE`, `WT_BTREE_SYNC`, `WT_BTREE_CHECKSUM`, `WT_EVICT_WALK_TYPE`, btree id namespace helpers, fixed shared table ids, the `WT_BTREE` struct, sync safety macros, clean-checkpoint timer macros, btree flags, `WT_SALVAGE_COOKIE`, page-delta enablement macros, and merge-state structs for applying leaf deltas to base images.

## Control Flow
The header is declarative, but `WT_BTREE` fields drive major flows. Search and reconciliation use type, key/value formats, collator, split settings, compression/encryption, max page sizes, and root ref. Checkpoint flows use `ckpt`, `checkpoint_gen`, `syncing`, clean checkpoint timers, write generations, and rec max transaction/timestamp. Eviction uses the tail fields after `WT_BTREE_CLEAR_SIZE`: current walk ref, soft normalized position, walk direction, progress/target/period, disabled/busy counters, and priority. Disaggregated flows use fixed shared ids, page log, next page id, reconciliation LSN, storage tier, and delta enablement.

## State And Persistence Behavior
Btree id and namespace values are persistent identity for local, shared, and special shared tables. Page size limits and checksum/compression/encryption settings shape on-disk page images. `write_gen`, `base_write_gen`, and checkpoint state track durable evolution. `file_max` currently bounds history-store size. Eviction fields are runtime-only and explicitly placed after `WT_BTREE_CLEAR_SIZE` so handle reset can preserve only the intended prefix. Disaggregated special ids are explicitly compatibility-sensitive.

## Dependencies And Integration Points
`WT_BTREE` embeds a root `WT_REF` from `btmem.h`, points to `WT_BM` from `block.h`, and references checkpoint, compressor, encryptor, bucket storage, page log, data handle, collator, and storage-tier types. It is used by almost every btree subsystem: cursor search, reconciliation, eviction, checkpoint, salvage, verify, history store, rollback, tiered/disaggregated storage, and cache accounting.

## Risks
Changing persistent ids, version bounds, page size limits, or flag values can break compatibility. The btree struct has mixed protected and shared fields; incorrect atomic/lock usage can corrupt cache accounting or sync/eviction coordination. Eviction state is owned by eviction, not generic btree code, so unrelated reset paths must respect `WT_BTREE_CLEAR_SIZE`. Disaggregated delta enablement must match page type and connection configuration.

## Test Signals
Test open/upgrade version bounds, special shared id stability, checksum/compression/encryption configurations, page-size validation, checkpoint sync state transitions, clean checkpoint timer behavior, eviction walk state reset/restore, btree eviction-disabled paths, cache byte accounting, history-store `file_max`, disaggregated page id/LSN allocation, and delta merge behavior for base plus leaf/internal deltas.
