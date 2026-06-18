<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py

Purpose: Thread helpers for tests that need concurrent checkpoints, tier flushes, backups, or mixed table operations while retaining access to the current `WiredTigerTestCase`.

Important APIs and types: `Thread` wraps `threading.Thread` and installs the captured current testcase in thread-local storage before running. Worker classes include `checkpoint_thread`, `named_checkpoint_thread`, `flush_checkpoint_thread`, `backup_thread`, and `op_thread`.

Control flow: Checkpoint threads open their own sessions and loop until a `done` event is set, optionally stopping after `checkpoint_count_max`. `flush_checkpoint_thread` randomly chooses normal checkpoint or `flush_tier=(enabled)`. `backup_thread` periodically rebuilds a backup directory, copies files from a backup cursor, opens the backup home, and compares live and backup tables. `op_thread` drains a queue of operation tuples for group insert/update, insert, session bounce, drop, or create-table-and-insert.

State and persistence behavior: Threads create independent sessions on a shared connection. Backup threads delete/recreate backup directories and copy WiredTiger files. Operation threads mutate tables and metadata concurrently. `checkpoint_count` records progress for bounded checkpoint tests.

Dependencies and integration points: Uses `wiredtiger`, `wttest`, `helper.compare_tables`, Python `queue`, `threading.Event`, and the suite thread-local current testcase used by hooks/utilities.

Risks: Threads swallow some `WiredTigerError` cases intentionally during drop/create races, which can hide unexpected errors if tests do not assert final state. Backup verification assumes file URIs from copied files and skips `WiredTiger*` metadata names. Fast checkpoint loops can amplify timing sensitivity.

Test signals: Thread completion, checkpoint counters, queue drain/task_done behavior, backup/live table comparisons, and absence of unhandled thread exceptions provide validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtthread.py -->
