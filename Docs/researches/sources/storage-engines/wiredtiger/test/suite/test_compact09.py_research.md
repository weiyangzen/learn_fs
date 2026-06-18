# sources/storage-engines/wiredtiger/test/suite/test_compact09.py

Purpose: tests background compaction exclude-list behavior.

Important APIs and types: `compact_util`, `stat.conn.background_compact_skipped_exclude`, `session.compact(None, background=true, exclude=...)`, `get_files_compacted`, and `get_pages_rewritten`.

Control flow: create two tables, populate and checkpoint, delete 90 percent from both, checkpoint, run background compaction once excluding both files and assert no files compacted; then run again excluding only the first file and verify only the second is compacted.

State and persistence behavior: background compaction should respect metadata/file-name exclude list and leave excluded table file pages unreclaimed.

Dependencies and integration points: background compaction, metadata file naming (`table:test_compact09_0.wt`), exclusion skip statistic, and helper stats. Tiered hook is skipped.

Risks: exclude strings use `.wt` file names derived from table URIs, so naming changes could break it. Asynchronous waits depend on background thread progress.

Test signals: exclude skip count equals expected cumulative values; first table has zero pages rewritten; second has positive pages rewritten.
