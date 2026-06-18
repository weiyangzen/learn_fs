# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover13.py

Purpose: regression coverage for history-store orphans surviving disaggregated step-up drain because prepared metadata on ingest btrees was hidden or lost.

Important APIs and types: helper methods `open_follower`, `create_hs_orphan_and_close_leader`, `finish_leader_checkpoint_and_close`, `trigger_panic_via_eviction`, `prepared_discover:`, `claim_prepared_id`, `wiredtiger.stat.conn.cache_hs_insert`, eviction debug cursors, and disaggregated role reconfiguration.

Control flow: `create_hs_orphan_and_close_leader` builds a version chain with committed `v_base`, committed `v0`, and prepared `v1`, advances stable, evicts under `ignore_prepare=true`, and asserts HS insertion. Path 1 checkpoints at prepare timestamp, follower claims and commits, writes `v2`/`v3`, advances oldest/stable so the version cursor might truncate, steps up, then writes `v4`/`v5` and evicts. Path 2 checkpoints later, claims/commits, writes `v2`/`v3`, evicts the ingest page so prepared id metadata could be dropped, steps up, then triggers eviction.

State and persistence behavior: the central state is an HS record whose stop timestamp would remain orphaned unless step-up drain sees the resolved prepared entry with its prepared id. Correct behavior is absence of panic during later eviction.

Dependencies and integration points: history store, prepared metadata, ingest btree, disaggregated follower-to-leader step-up, eviction, and statistics.

Risks: this is a negative regression test where the main symptom is no crash. It depends on carefully constructed timestamp and eviction order.

Test signals: HS insertion statistic is positive, discover finds at least one id, and the final eviction sequence completes without out-of-order timestamp panic.
