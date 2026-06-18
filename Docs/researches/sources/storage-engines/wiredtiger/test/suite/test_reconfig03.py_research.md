# sources/storage-engines/wiredtiger/test/suite/test_reconfig03.py

Purpose: mirrors MongoDB-style connection reconfiguration workloads, changing eviction/cache/shared-cache settings while a populated table and periodic checkpoints are active.

Important APIs and types: `SimpleDataSet.populate`, `time.sleep`, `self.conn.reconfigure`, log/checkpoint/cache connection config, and checkpoint log-size config.

Control flow: `test_reconfig03_mdb` populates increasing numbers of rows, sleeps to allow checkpoint activity, and reconfigures `eviction_target`, `cache_size`, `eviction_dirty_target`, and `shared_cache`. `test_reconfig03_log_size` reconfigures checkpoint log-size thresholds among small, 1M, and zero.

State and persistence behavior: table contents grow while background checkpointing and logging are enabled. The test stresses runtime config changes under active data modification.

Dependencies and integration points: cache sizing, eviction thresholds, checkpoint thread, shared cache parser, logging, and dataset population.

Risks: sleeps make it timing-dependent, but the goal is smoke coverage rather than exact statistics.

Test signals: all reconfiguration calls and subsequent population phases complete without error.
