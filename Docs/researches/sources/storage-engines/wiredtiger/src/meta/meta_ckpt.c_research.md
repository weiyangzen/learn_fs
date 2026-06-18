# sources/storage-engines/wiredtiger/src/meta/meta_ckpt.c

## Purpose
Owns parsing, validating, querying, and rewriting checkpoint-related metadata for btree files and system checkpoint state. It translates metadata config strings into `WT_CKPT` structures and serializes updated checkpoint lists, timestamps, snapshots, live-restore metadata, and incremental-backup block-modification information back into metadata.

## Important APIs, Types, and Functions
Major APIs include `__wt_meta_checkpoint`, `__wt_meta_checkpoint_last_name`, `__wt_meta_checkpoint_by_name`, `__wt_meta_checkpoint_clear`, `__wt_ckpt_last_name`, `__wt_ckpt_last_size`, `__wt_meta_ckptlist_get`, `__wt_meta_ckptlist_get_from_config`, `__wt_meta_ckptlist_to_meta`, `__wt_meta_ckptlist_update_config`, `__wt_meta_ckptlist_set`, `__wt_meta_sysinfo_set`, `__wt_meta_sysinfo_clear`, `__wt_meta_read_checkpoint_snapshot`, `__wt_meta_read_checkpoint_timestamp`, `__wt_meta_read_checkpoint_oldest`, `__wt_meta_load_prior_state`, `__wt_meta_correct_base_write_gen`, and `__wt_reset_blkmod`. Important private helpers include `__ckpt_load`, `__ckpt_last`, `__ckpt_named`, `__ckpt_set`, `__ckpt_version_chk`, `__meta_blk_mods_load`, `__ckpt_blkmod_to_meta`, and `__ckpt_parse_time`.

## Control Flow
Read paths fetch a metadata config with `__wt_metadata_search`, check btree version compatibility, parse the `checkpoint` config array, and select either a named checkpoint or the highest-order checkpoint. List paths either reuse `btree->ckpt` or rebuild from config, sorting by order and optionally allocating a new add checkpoint. Write paths convert a `WT_CKPT` list to `checkpoint=(...)`, append live-restore and `checkpoint_backup_info` strings when needed, add a checkpoint LSN if supplied, and call `__ckpt_set` to collapse the new config into the file metadata. System info paths write or remove `system:checkpoint`, `system:oldest`, and `system:checkpoint_snapshot` entries, including named variants.

## State and Persistence Behavior
The file persists checkpoint addresses, raw cookies as hex strings, order, wall-clock time, size, time aggregates, write generations, run write generations, disaggregated next page IDs, checkpoint LSNs, incremental backup block bitmaps, encrypted block metadata, live-restore file-handle metadata, checkpoint timestamps, oldest timestamps, snapshot arrays, and base write generation. It updates connection state such as `base_write_gen` and `ckpt.most_recent` from prior metadata at startup and after recovery.

## Dependencies and Integration Points
It depends on the metadata table layer, config parser/collapser, btree/block manager checkpoint state, encryption helpers, live restore, tiered/disaggregated storage, incremental backup, timestamp parsing, transaction snapshot data, and version compatibility definitions. It is central to checkpoint, recovery, backup, rollback-to-stable, live restore, and startup compatibility checks.

## Risks and Edge Cases
Unsigned wall-clock times are parsed manually because config numeric values are signed. Backward compatibility is maintained for older durable timestamp field names and missing runtime write generation or `next_page_id`. Cached checkpoint lists must match metadata; diagnostic validation compares both paths. `__ckpt_set` can use the dhandle metadata base fast path but panics if the base hash changed unexpectedly. Incremental backup block-mod state must be reset when IDs change or files are renamed. Snapshot parsing assumes count/list consistency. System timestamp entries are removed instead of storing zero to preserve downgrade compatibility.

## Test Signals
Strong signals include checkpoint/restart/recovery suites, named checkpoint queries, timestamp and snapshot recovery tests, compatibility/downgrade tests, incremental backup rename/reset tests, encrypted metadata tests, live-restore metadata tests, disaggregated checkpoint size accounting, and diagnostic checkpoint validation comparing cached and rebuilt lists.
