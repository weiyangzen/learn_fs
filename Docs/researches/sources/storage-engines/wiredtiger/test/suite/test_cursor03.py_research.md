<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor03.py

Purpose: extends cursor insert/remove/iteration testing to larger tables and varied key/value sizes.

Important APIs and control flow: inherits `TestCursorTracker`, with scenarios for row/column tables, 1000/10000 entries, and large value or key/value sizes up to 10000 bytes. It creates the table with scenario formats, seeds tracker state, opens with append, then runs multiple-remove and insert/remove sequences similar to cursor02 across larger data.

State, persistence, and dependencies: persistent state may include large keys and values, stressing page layout and cursor movement. Dependencies are `TestCursorTracker`, `make_scenarios`, inherited `config_string`, and WT cursor append/iteration APIs.

Integration points: covers access-method behavior under larger payloads and cardinalities, including insert ordering and removal navigation.

Risks and test signals: large scenarios increase runtime and cache/page pressure. Pass signals are tracker-valid forward/backward order and consistency after repeated modifications across both small and large records.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor03.py -->
