# sources/storage-engines/wiredtiger/test/suite/test_checkpoint14.py

Purpose: verifies each checkpoint has its own snapshot by creating two successive checkpoints while transactions commit concurrently and then reading both.

Important APIs/types/functions: `checkpoint_thread`, `named_checkpoint_thread`, `stat.conn.checkpoint_state`, `timing_stress_for_test=[checkpoint_slow]`, `simulate_crash_restart`, `SimpleDataSet`, and precise/fuzzy scenarios.

Control flow: write baseline `value_a` and checkpoint, start a transaction writing all rows to `value_b`, start first checkpoint thread and wait until active, commit transaction, repeat with `value_c` and the second checkpoint, then read the first checkpoint expecting all `value_a` and the second expecting all `value_b`. Finally simulate crash/restart; the RTS consistency statistic check is present but disabled.

State/persistence behavior: each checkpoint must retain the snapshot it was created with and not accidentally use a later checkpoint's visibility state.

Dependencies/integration: named/unnamed checkpoint combinations, checkpoint concurrency, snapshot isolation, crash restart helper, and hook skips.

Risks/test signals: comments note timing lag could make the race less deterministic. Assertions focus on snapshot separation rather than torn transaction detection.
