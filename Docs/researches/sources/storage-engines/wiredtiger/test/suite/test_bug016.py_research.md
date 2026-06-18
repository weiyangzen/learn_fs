# sources/storage-engines/wiredtiger/test/suite/test_bug016.py

Purpose: regression for WT-2757 covering when `WT_CURSOR.get_key()` is valid after `insert`. The valid case is append-mode record-number column store; non-append and row-store inserts should require the key to be set again.

Important APIs/types/functions: `wiredtiger.WiredTigerError`, `session.create`, `session.open_cursor`, cursor `set_key`, `set_value`, `insert`, `get_key`, and `assertRaisesWithMessage`.

Control flow: six methods cover simple file column store append, simple column store non-append, simple row store, complex table column store append, complex column store non-append, and complex row store. Append cases assert returned key `1`; all others expect `/requires key be set/`.

State/persistence behavior: writes a single record per case, but persistence is incidental. The tested state is cursor key retention after insert across URI kind and key format.

Dependencies/integration: exercises both file and table cursors, record-number allocation, append cursor configuration, and error handling.

Risks/test signals: depends on exact cursor API semantics. Any API broadening that preserves keys after non-append inserts would need corresponding test intent review.
