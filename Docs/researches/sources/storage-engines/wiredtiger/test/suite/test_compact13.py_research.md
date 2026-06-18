# sources/storage-engines/wiredtiger/test/suite/test_compact13.py

Purpose: checks that background compaction statistics/state reset after the server is disabled, so later eligible files can be compacted rather than treated as already processed/skipped.

Important APIs and types: `compact_util`, `turn_on_bg_compact`, `turn_off_bg_compact`, `get_bg_compaction_files_skipped`, `get_files_compacted`, and background compact free-space target.

Control flow: create two tables and populate them without deleting data, checkpoint, enable background compaction and wait until tables plus history store are skipped, disable it, delete 90 percent of both tables, checkpoint, re-enable background compaction, and wait until both files are compacted.

State and persistence behavior: background compaction server lifecycle should clear relevant per-run state so subsequent runs can process changed files.

Dependencies and integration points: background compaction asynchronous state, skip counters, compact utility deletion/population, and table stats. Tiered hook is skipped.

Risks: no explicit final assert beyond waiting for compaction count; timeout behavior depends on test harness. Imports `stat` but does not use it directly.

Test signals: the waits complete: initial skip count reaches `n_tables + 1`, and after deletion `get_files_compacted(uris)` reaches 2.
