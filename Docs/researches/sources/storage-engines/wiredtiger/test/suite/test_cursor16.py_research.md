<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor16.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor16.py

Purpose: ensures final session close releases cached cursors and leaves zero cached cursor count.

Important APIs and control flow: connection enables cursor caching, fast stats, and in-memory mode. For 100 URIs, the main session creates tables and holds one open cursor per URI. Then 100 additional sessions each open/read/close a cursor for every URI, populating per-session cursor caches. Closing all auxiliary sessions should drain cached cursors; the test asserts `cursor_cached_count` is 0 before and after.

State, persistence, and dependencies: state is in-memory table data, many sessions, held dhandle references, and cursor cache statistics. Dependencies are `wiredtiger.stat`, session open/close, and key-format scenarios for row/var.

Integration points: covers cursor cache cleanup during session close and protection against swept dhandles while main cursors are open.

Risks and test signals: large session*URI count can be resource-heavy. Pass signal is exact zero cached cursor count after closing all sessions, indicating no final-close leak.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor16.py -->
