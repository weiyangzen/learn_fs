# sources/storage-engines/wiredtiger/test/suite/test_compact14.py

Purpose: verifies background compaction skips small files that do not meet compaction thresholds.

Important APIs and types: `compact_util`, `turn_on_bg_compact`, `get_bg_compaction_files_skipped`, `session.checkpoint`, and table creation/population helpers.

Control flow: create a small table with one key, checkpoint it to disk, enable background compaction with `free_space_target=1MB`, then wait until at least one file is counted as skipped.

State and persistence behavior: no meaningful reclaimable space exists; the background server should inspect and skip rather than rewrite.

Dependencies and integration points: background compaction threshold logic and skip statistics. Tiered hook is skipped.

Risks: the test is wait-only with no explicit assert after the loop; a hang is the failure mode. The skipped file could be the tiny table or another small internal file depending on metadata traversal.

Test signals: `get_bg_compaction_files_skipped()` becomes nonzero.
