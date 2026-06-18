# sources/storage-engines/wiredtiger/test/suite/test_layered_eviction02.py

Purpose: verifies clean eviction can occur on a follower/standby without explicitly setting a page materialization frontier.

Important APIs and functions: `test_layered_eviction02` uses leader and follower disaggregated connection configs, `disagg_advance_checkpoint`, `stat.conn.cache_eviction_clean`, debug eviction with `debug=(release_evict_page)`, and timestamped leader writes.

Control flow: the leader creates a table, inserts a small timestamped dataset, sets stable timestamp, checkpoints, and advances a follower. The follower opens a debug eviction session and evicts a key. The test reads follower statistics and asserts clean eviction increased.

State and persistence behavior: all data is stable checkpointed state. The follower should be able to discard clean pages without a materialization frontier because no dirty or ahead-of-frontier page state is involved.

Dependencies and integration: depends on follower checkpoint synchronization, eviction debug hooks, clean eviction stats, and layered/disaggregated table visibility. Risks include overly conservative frontier checks that block clean eviction or follower eviction paths that require unavailable leader-only state. Test signals are successful eviction search and positive `cache_eviction_clean`.
