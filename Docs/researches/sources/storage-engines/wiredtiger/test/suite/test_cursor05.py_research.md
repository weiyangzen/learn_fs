<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor05.py

Purpose: validates cursor uninitialized/end-position behavior and iteration over tables with optional column groups.

Important APIs and control flow: scenarios cover row versus column keys, empty versus three-entry tables, and no/two/four column groups. The test builds a table with composite columns, creates colgroups when configured, populates rows, and calls `check_entries()` for forward and backward scans after initial unpositioned state, after next/prev endpoint round-trips, after reset, and after completed iteration.

State, persistence, and dependencies: persistent state includes main table rows and optional colgroup objects. Dependencies are `wttest`, `make_scenarios`, cursor tuple key/value APIs (`get_keys`, `get_values`), and column-group projection.

Integration points: covers cursor reset/uninitialized state, endpoint movement, full scans, composite row/table schemas, and colgroup-backed reads.

Risks and test signals: column and row cursors expose different key shapes, increasing assertion complexity. Pass signals are stable forward/backward ordering and no stale position after reset or endpoint traversal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor05.py -->
