# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable05.py

Purpose: exercises rollback-to-stable (RTS) when two tables have unstable updates while another session holds a long-running transaction open. It varies column-store versus integer row-store keys, in-memory versus disk-backed connections, prepared versus non-prepared updates, and RTS worker thread counts 0/4/8.

Important APIs/types/functions: class `test_rollback_to_stable05` extends `test_rollback_to_stable_base`, reusing `large_updates`, `check`, `timestamp_str`, and RTS log verification. `conn_config` enables `statistics=(all)` and `verbose=(rts:5)`, plus `in_memory=true` for that scenario. The test uses `SimpleDataSet`, explicit `session.checkpoint`, an auxiliary session transaction, `conn.rollback_to_stable('threads=N')`, and `stat.conn.txn_rts*` counters.

Control flow: creates two tables, pins oldest/stable at timestamp 10, writes table 1 at 20/30/40/50, opens a second session transaction, writes table 2 at 20/30/40/50, optionally checkpoints for disk cases, commits the long transaction, then runs RTS. Visibility checks before RTS prove each timestamped value is readable; checks after RTS expect both tables to remain at their stable view rather than being incorrectly affected by the formerly open transaction.

State and persistence behavior: disk cases force dirty pages through checkpoint before RTS; in-memory cases skip checkpoint and therefore have different aborted-update expectations. Prepared scenarios offset read timestamps and use durable timestamps through the shared helper. Persistence-sensitive state is the combination of data-store pages, history-store records, active transaction visibility, and RTS statistics.

Dependencies and integration points: integrates with WiredTiger Python test harness, `wtdataset.SimpleDataSet`, `wtscenario.make_scenarios`, `wiredtiger.stat`, and helper-level RTS log verification. It is a direct regression for transaction ID visibility crossing multiple dhandles during RTS.

Risks: sensitive to transaction lifetime cleanup and checkpoint timing. If RTS starts with a live transaction or stats are interpreted identically for in-memory and disk modes, false failures can occur. Worker-thread variants increase coverage for parallel tree traversal races.

Test signals: asserts one RTS call, no key removal/restoration, nonnegative pages visited, and mode-dependent `txn_rts_upd_aborted` behavior. Data checks around timestamps are the primary correctness signal.
