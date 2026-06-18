<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py

Purpose: Shared base support for rollback-to-stable Python tests. It supplies repeatable bulk update/modify/remove helpers, read-at-timestamp validation, eviction forcing, and a teardown verifier that runs the RTS log verifier against `stdout.txt`.

Important APIs and types: `get_git_root`, `get_rts_verify_path`, and `verify_rts_logs` locate and run `tools/rts_verifier/rts_verify.py`. `test_rollback_to_stable_base` extends `wttest.WiredTigerTestCase`, ignores RTS/read verbose output, installs `verify_rts_logs` as a teardown action, and exposes `retry_rollback`, `large_updates`, `large_modifies`, `large_removes`, `check`, and `evict_cursor`.

Control flow: Tests subclass the base, use `large_*` helpers to write many keys under normal, no-timestamp, or prepared timestamped transactions, then call WiredTiger rollback-to-stable APIs elsewhere. `retry_rollback` reruns a callable up to 100 times on `WT_ROLLBACK`, rolling back and reopening a transaction when a session is supplied. `check` scans at a read timestamp and verifies value/count invariants.

State and persistence behavior: The helper mutates real WiredTiger tables and timestamps commits using `timestamp_str`. Prepared updates use prepare, commit, and durable timestamps. `evict_cursor` opens `debug=(release_evict)` and resets periodically inside an `ignore_prepare=true` transaction to push data out of cache before rollback-to-stable validation. The teardown verifier treats stdout verbose logs as a persistent test signal.

Dependencies and integration points: Depends on `wiredtiger`, `wttest`, `WT_ROLLBACK` error strings, the RTS verifier script, and dataset objects that provide `key(i)`. It integrates with the suite teardown-action contract in `WiredTigerTestCase`.

Risks: Retry detection depends on localized/stringified rollback messages. A failed helper operation can leave an open transaction unless the rollback branch runs. The verifier path falls back relative to this helper if Git discovery fails, so repository layout changes can break teardown verification.

Test signals: Successful tests have no RTS verifier errors, expected row counts at read timestamps, exact values after rollback-to-stable, and no exhausted retry loops.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/rollback_to_stable_util.py -->
