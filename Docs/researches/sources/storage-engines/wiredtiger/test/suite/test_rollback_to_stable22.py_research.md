# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable22.py

Purpose: stress test for RTS transaction checks while many dhandles and eviction/history-store activity exist. It is designed to make eviction active without letting history-store work interfere with RTS's active transaction validation.

Important APIs/types/functions: extends the RTS base, uses `SimpleDataSet`, repeated large updates across several datasets, `conn.rollback_to_stable('threads=N')`, and scenario worker thread counts. The class sets `conn_config` directly to `cache_size=100MB,verbose=(rts:5)` and disables prepare.

Control flow: creates several tables, populates each, then runs many iterations of 100-byte updates across 1,000 rows to generate around 100MB of activity and trigger eviction. RTS is then invoked under different worker counts.

State and persistence behavior: focuses on concurrent internal state: multiple open dhandles, eviction, history-store activity, and RTS transaction validation. The tables are not primarily used for detailed timestamp visibility checks.

Dependencies and integration points: depends on the shared RTS base, WiredTiger eviction behavior, and the scenario framework. It complements functional rollback tests by exercising resource/transaction coordination.

Risks: workload size and cache behavior make it timing-sensitive. If eviction thresholds or cache behavior change, the intended pressure may weaken.

Test signals: absence of illegal active-transaction failures or data corruption during RTS is the primary signal; scenario completion under all thread counts is meaningful.
