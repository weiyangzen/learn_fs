# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs04.py

Purpose: tests reading prepared updates from disk with `ignore_prepare`, and resolving prepared inserts over keys that already have tombstones, including crash/restart rollback-to-stable behavior.

Important APIs and types: `copy_wiredtiger_home`, `wiredtiger.stat.conn.cache_write_hs`, `search_keys_timestamp_and_ignore`, `prepare_updates`, debug `release_evict_page`, transaction configs with `ignore_prepare=true/false`, and commit/rollback scenarios.

Control flow: it inserts committed values at timestamp 2, checkpoints, removes them at timestamp 10, advances stable, then opens multiple prepared sessions inserting the same keys at timestamp 20. It reads at timestamp 5 and 20 with/without `ignore_prepare`, optionally commits prepared transactions at timestamp 30, checkpoints, copies the home to `RESTART`, reopens, and validates reads at timestamps 5, 20, and 30.

State and persistence behavior: the test covers prepared updates written to disk over an existing tombstone and how recovery/rollback-to-stable restores or commits them. It distinguishes pre-delete value, deleted state, prepare conflicts, and committed prepare values.

Dependencies and integration points: history store, tombstones, eviction, prepared transaction resolution, crash-copy recovery, and RTS. It is skipped for disaggregated hooks because RTS is not used there.

Risks: many assertions depend on exact timestamp order and `ignore_prepare` semantics. Misordered stable timestamps could obscure whether prepared state or tombstone state is being read.

Test signals: prepare conflicts occur only with `ignore_prepare=false` before resolution; after restart, committed scenarios show prepared values at timestamp 30 and rollback scenarios show `WT_NOTFOUND`.
