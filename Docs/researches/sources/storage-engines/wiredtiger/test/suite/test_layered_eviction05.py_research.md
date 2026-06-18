# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction05.py

Purpose: ensures obsolete time window cleanup is not reviewed for read-only btrees on followers.

Important APIs and functions: `test_layered_eviction05` inherits `eviction_util` and `WiredTigerTestCase`, uses leader and follower disaggregated configs, `stat.conn.cache_eviction_dirty_obsolete_tw`, `stat.dsrc.cache_eviction_dirty_obsolete_tw`, helper `read`, and `get_stat` from eviction utilities.

Control flow: the leader/follower setup writes checkpointed data, the follower reads rows to bring pages into cache, and the test checks obsolete time window eviction statistics. It expects no dirty obsolete-time-window cleanup activity for the follower read-only btree path.

State and persistence behavior: the follower should observe stable checkpointed data without making btree pages dirty for obsolete time window cleanup. The test guards a read-only invariant: follower reads must not trigger dirty reconciliation work that belongs to writable btrees.

Dependencies and integration: integrates eviction utility helpers, follower connection config, layered table reads, and eviction/time-window stats. Risks include read-only follower pages being dirtied, unexpected reconciliation on followers, and stat accounting regressions. Test signals are zero equality assertions for obsolete time-window dirty eviction stats.
