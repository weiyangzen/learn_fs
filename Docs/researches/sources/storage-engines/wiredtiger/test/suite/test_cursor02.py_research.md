<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_cursor02.py

Purpose: uses `TestCursorTracker` to validate cursor insert/remove/iteration behavior on small row and column tables.

Important APIs and control flow: `create_session_and_cursor()` creates a table with row or record-number keys, seeds tracker state via `cur_initial_conditions`, and opens with `append`. Tests delete multiple adjacent positions, insert records around a position, move forward/backward, and exercise empty and one-record tables. Tracker helpers perform expected-position and content checks.

State, persistence, and dependencies: state is both persistent table content and the base tracker model of expected keys/values. Dependencies include `TestCursorTracker`, `wiredtiger.WT_NOTFOUND`, `make_scenarios`, and cursor append mode.

Integration points: covers cursor state transitions after remove/insert, boundary movement, empty table iteration, and both row and column access methods.

Risks and test signals: much behavior is hidden in the tracker base class; local failures may be caused by model drift. Pass signals are tracker-confirmed contents and correct `WT_NOTFOUND` at first/last on empty inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_cursor02.py -->
