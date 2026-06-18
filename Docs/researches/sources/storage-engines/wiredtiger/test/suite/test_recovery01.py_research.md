# sources/storage-engines/wiredtiger/test/suite/test_recovery01.py

Purpose: tests recovery/shutdown progress logging while validating logged and non-logged table recovery semantics across crash-style and clean reopen paths.

Important APIs and types: `simulate_crash_restart`, `SimpleDataSet`, `stat`, `make_scenarios`, `large_updates`, `check`, verbose config `recovery_progress`, and log-enabled connection config.

Control flow: it creates one logged table and one non-logged table, pins oldest/stable to 1, writes value A and value B to both tables, using timestamps only for the non-logged table. It sets stable to 10, checkpoints, then either simulates a crash restart or cleanly reopens. It checks logged table keeps the latest value B while non-logged table rolls back to stable value A at timestamps 10 and 20.

State and persistence behavior: logged table updates are recovered from logs; non-logged timestamped updates beyond stable are rolled back to stable on recovery. The test also suppresses expected recovery-progress stdout.

Dependencies and integration points: logging, recovery, rollback-to-stable during recovery, timestamped non-logged tables, crash simulation, and verbose recovery messages.

Risks: this test assumes stable timestamp 10 should make value B at timestamp 20 disappear for non-logged data while logged data remains durable.

Test signals: post-restart logged reads return value B for all rows; non-logged reads return value A at both read timestamps.
