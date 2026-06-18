# sources/storage-engines/wiredtiger/test/suite/test_cc01.py

Purpose: shared base utilities for checkpoint-cleanup tests. It centralizes update generation, modify generation, timestamped reads, table population, and checkpoint-cleanup triggering/stat validation.

Important APIs/types/functions: class `test_cc_base`, `get_stat`, `large_updates`, `large_modifies`, `check`, `populate`, `wait_for_cc_to_run`, and `check_cc_stats`. It uses `wiredtiger.Modify`, `stat.conn.checkpoint_cleanup_success`, `checkpoint_cleanup_pages_visited`, and `checkpoint_cleanup_pages_removed`.

Control flow: helpers open cursors, commit per-row timestamped updates, apply modify lists in one transaction, scan at read timestamps, and force cleanup via `session.checkpoint("debug=(checkpoint_cleanup=true)")`, optionally with a checkpoint name. `wait_for_cc_to_run` loops until the success counter advances.

State/persistence behavior: supports tests that create history-store content and then drive cleanup. The base itself has no tests but defines the state transitions used by `test_cc02` and later files.

Dependencies/integration: imported directly by sibling checkpoint-cleanup tests, relying on statistics cursors and debug checkpoint configuration.

Risks/test signals: if stat names or debug config change, all dependent cc tests can hang or fail. The waiting loop has no explicit timeout.
