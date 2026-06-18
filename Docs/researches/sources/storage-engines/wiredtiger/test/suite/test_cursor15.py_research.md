<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor15.py

Purpose: smoke-tests the cursor `read_once=true` configuration under small-cache table scans and cursor caching.

Important APIs and control flow: with `cache_size=1M`, the test creates a table tuned to roughly one 100KB page per document, inserts 20 large records, reopens to clear cache, then scans the table once with `read_once=true` and once with default cursor config without restarting between scans.

State, persistence, and dependencies: persistent state is 2MB of table data; transient state is cache pressure from scanning pages larger than cache capacity. Dependencies are `wttest`, table page-size config, cursor open config, and full-table iteration.

Integration points: covers `WT_READ_WONT_NEED`-style cursor behavior and compatibility with cursor caching/reuse.

Risks and test signals: there is no statistic assertion, so this is mainly a crash/regression smoke test. Pass signal is successful scans with and without `read_once` under constrained cache.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor15.py -->
