# sources/storage-engines/wiredtiger/test/suite/test_compact04.py

Purpose: checks accuracy of compact work estimation by comparing expected rewritten pages with actual rewritten pages over repeated table instances.

Important APIs and types: `compact_util`, `stat.dsrc.btree_compact_pages_rewritten`, `btree_compact_pages_rewritten_expected`, `btree_compact_pages_selected_inmem`, `stat.conn.session_table_compact_bytes_rewrite_inmem`, and verbose compact output suppression.

Control flow: for up to 10 iterations, create and populate a table, checkpoint, delete several ranges to create reclaimable space, compact, read data-source and connection stats, compute prediction error, and terminate early if prediction is good with no failures.

State and persistence behavior: compaction estimation and actual rewriting are both tracked in statistics. The test tolerates rare inaccurate predictions but caps failures.

Dependencies and integration points: compact progress verbose/stat infrastructure, in-memory page selection, and `compact_util.populate`.

Risks: prediction accuracy is intentionally probabilistic; up to two failures are tolerated. Tiered storage returns early after gathering stats because compact stats are not meaningful there.

Test signals: non-tiered runs require positive rewritten/expected/selected stats and prediction error under 15 percent for at least one iteration before too many failures.
