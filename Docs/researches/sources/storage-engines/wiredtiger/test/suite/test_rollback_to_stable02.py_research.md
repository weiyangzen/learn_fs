# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable02.py

Purpose: verifies rollback-to-stable replaces newer on-disk values with the stable history-store value after multiple full updates.

Important APIs and types: `test_rollback_to_stable_base`, `large_updates`, `check`, `conn.rollback_to_stable`, dryrun/thread scenarios, in-memory/prepared scenarios, and RTS statistics including update-aborted and HS-removed counters.

Control flow: it writes four full-value generations at timestamps 10, 20, 30, and 40. Stable is set to 30 for prepared mode or 20 otherwise, the table is checkpointed when not in-memory, and RTS is run. Dryrun expects the latest value to remain; real RTS expects value B to be visible even at a later read timestamp. It also verifies older timestamp reads.

State and persistence behavior: newer updates beyond the stable point must be removed from both update chains and history store as appropriate, leaving the stable full value visible.

Dependencies and integration points: RTS history restore, dryrun accounting, prepared timestamp adjustment, in-memory mode, and worker-thread variants.

Risks: this test counts at least two generations per row as aborted/removed; internal history-store accounting changes may require stat expectation updates.

Test signals: post-RTS reads return value B unless dryrun, calls equal 1, pages visited is positive, and update-aborted/dryrun counters are at least `nrows * 2` in the expected branch.
