<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor01.py

Purpose: basic smoke test for file/table cursors over row and column stores, including key/value state, forward/backward iteration, cursor duplication, and comparison.

Important APIs and control flow: scenarios cover `file:`/`table:` plus row/string and column/record-number formats. Helpers create and populate 10 records, assert unpositioned cursors have no key/value, iterate with `next()` or `prev()`, check `WT_NOTFOUND` at endpoints, duplicate positioned cursors via `open_cursor(None, cursor, None)`, and compare duplicate positions.

State, persistence, and dependencies: persistent state is a small object populated through cursor assignment. Dependencies are `wiredtiger`, `wttest`, `make_scenarios`, cursor URI exposure, `recno()`, and duplicate-cursor support. Layered/disagg hooks skip duplicate assertions.

Integration points: covers core WT_CURSOR positioning, `get_key`, `get_value`, endpoint reset semantics, duplication, and comparison for access methods.

Risks and test signals: duplicate support differs for layered tables. Pass signals are exact key/value order, no stale key/value after reset/endpoints, and equal duplicate cursor positions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor01.py -->
