# sources/storage-engines/wiredtiger/test/suite/test_hs_evict_race01.py

Purpose: exercises a race between checkpoint, eviction, history-store activity, and no-timestamp updates. It uses checkpoint slowdown to widen the window.

Important APIs and functions: `test_hs_evict_race01` uses `timing_stress_for_test=(checkpoint_slow)`, scenarios for recno and integer row-store keys, `simulate_crash_restart`, and `wtthread` checkpoint threading. Main methods are `test_mm_ts` and `no_timestamp_update_and_evict`.

Control flow: the test creates a one-row table, writes timestamped values, starts or coordinates checkpoint activity, performs no-timestamp updates and debug eviction, then uses crash/restart simulation to verify durable state. The helper performs a no-timestamp update and evicts the page to force reconciliation while checkpoint timing is stressed.

State and persistence behavior: timestamped versions and later no-timestamp updates must maintain correct history-store and durable visibility across eviction and crash recovery.

Dependencies and integration points: integrates timing stress, checkpoint threads, debug eviction, crash-restart helper, timestamp APIs, and WiredTiger transaction visibility.

Risks and edge cases: race tests are sensitive to timing and scheduler behavior. With only one row, it targets a specific interleaving rather than broad page coverage.

Test signals: assertions validate expected values during the race and after restart; absence of crash/recovery errors is also a signal.
