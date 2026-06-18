# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor04.py

Purpose: basic layered cursor insert/read/traversal smoke test.

Important APIs/types/functions: uses `disagg_test_class`, layered verbose leader config, `session.create`, `open_cursor`, direct cursor item assignment, `set_key`, `search`, `get_value`, `reset`, `next`, `prev`, and close/reopen cursor flow.

Control flow: creates a layered table, opens a cursor, inserts three string key/value pairs, searches for `Hello`, reads value via both `get_value` and `cursor["Hello"]`, scans forward, scans backward, closes, reopens a cursor, and scans forward again.

State and persistence behavior: verifies in-memory/current-session layered cursor state for inserted rows and cursor traversal. No explicit checkpoint or follower pickup is used.

Dependencies/integration points: layered insert path, search path, bidirectional cursor iteration, cursor reset/reopen lifecycle, and disaggregated leader setup.

Risks: printed traversal is not asserted beyond lack of error, and the final reopened cursor is not closed in the source. It does not check exact scan order with assertions.

Test signals: pass means basic insert/search/scan operations on a leader layered cursor do not fail and return at least the searched value.
