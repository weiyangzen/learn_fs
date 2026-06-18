# sources/storage-engines/wiredtiger/test/suite/test_compact06.py

Purpose: tests background compaction API validation, running state errors, run-once behavior, and history-store skip accounting.

Important APIs and types: `session.compact(None, "background=true")`, `turn_on_bg_compact`, `turn_off_bg_compact`, `get_bg_compaction_files_skipped`, `get_bg_compaction_running`, `session.get_last_error`, `errno.EINVAL`, and `wiredtiger.WT_BACKGROUND_COMPACT_ALREADY_RUNNING`.

Control flow: assert background compaction cannot be started on a specific URI, cannot disable with extra configuration, and cannot exclude non-table URIs. Enable background compaction, verify reconfiguration attempts fail with specific sub-error, wait for HS skip, disable, run once, wait for self-stop, then enable/disable again.

State and persistence behavior: no user data is compacted; state is the background compaction server lifecycle and cumulative skip counters.

Dependencies and integration points: compact server configuration parser, error reporting, helper methods in `compact_util`, and background compaction statistics. Tiered hook is skipped.

Risks: waits depend on background thread scheduling. Uses `assert` for some checks rather than `self.assert*`.

Test signals: expected API errors occur, last-error subcode matches already-running, skip counter advances as expected, and run-once server stops.
