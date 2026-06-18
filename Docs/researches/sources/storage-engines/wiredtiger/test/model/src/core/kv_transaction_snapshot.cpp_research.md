# sources/storage-engines/wiredtiger/test/model/src/core/kv_transaction_snapshot.cpp

Purpose: implements transaction snapshot visibility predicates for model-generated snapshots and snapshots imported from WiredTiger metadata.

Important APIs and functions: `kv_transaction_snapshot_by_exclusion::contains` excludes updates whose transaction ID is newer than `_exclude_after` or appears in `_exclude_ids`. `kv_transaction_snapshot_wt::contains` first compares WiredTiger base write generation, then applies snapshot min/max and excluded ID set to WiredTiger transaction IDs.

Control flow and state: snapshots are immutable after construction. The WT-style snapshot treats older write generations as visible, newer generations as invisible, and only compares transaction IDs within the same write-generation era.

Dependencies and integration: used by `kv_database::txn_snapshot_nolock`, checkpoint creation, debug-log checkpoint metadata replay, and `kv_table_item` visibility filtering. Depends on `kv_update` methods exposing model and WT transaction metadata.

Risks and test signals: write-generation handling is critical after restart/log replay because transaction IDs alone are not globally meaningful. Incorrect max-exclusive behavior or exclusion set handling would surface as verification mismatches after checkpoints, recovery, or imported log snapshots.
