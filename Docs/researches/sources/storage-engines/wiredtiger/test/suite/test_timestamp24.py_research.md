<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py

Purpose: Verifies that a transaction reading an older version cannot later perform a conflicting update after a newer committed version has been reconciled.

Important APIs/types/functions: `test_timestamp24` uses two sessions, `SimpleDataSet`, timestamped commits, read timestamp transactions, cursor reset, `debug=(release_evict)`, and `WT_ROLLBACK` error checking.

Control flow: Session 1 writes value A at timestamp 20, then opens a read transaction at 25 and reads A while leaving the transaction open. Session 2 writes value B at timestamp 50 and evicts the page so B goes to disk and A goes to history. Session 2 rolls back a value C update. Session 1 then tries to write value D and must receive rollback. Final read at timestamp 60 expects value B unless the deliberately flagged broken path occurred.

State and persistence behavior: The page is reconciled while an older reader is open, creating a disk/history split. The test protects against applying an older transaction's update to the wrong version after reconciliation.

Dependencies and integration points: Integrates cursor reset/page unpinning, eviction, history-store placement, conflict detection, and multi-session transaction ordering.

Risks: The comments describe prior corruption where an update was applied to the newest version instead of the transaction's visible version. This is a data-corruption-sensitive test.

Test signals: A successful conflicting write is an explicit failure; final value comparison verifies the visible latest value remains B.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp24.py -->
