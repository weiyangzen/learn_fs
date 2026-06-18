# sources/storage-engines/wiredtiger/test/suite/test_checkpoint12.py

Purpose: validates that checkpoint cursor reads are forbidden after the owning session has prepared a transaction, preserving the blanket ban on operations after prepare.

Important APIs/types/functions: `make_scenarios` over cursor operations `search`, `next`, `prev`, `search_near`, `prepare_transaction`, checkpoint cursor `WiredTigerCheckpoint`, and `assertRaisesWithMessage`.

Control flow: create and populate a column-store table, set timestamps, write data at timestamp 10, checkpoint, write more data at timestamp 20, open a checkpoint cursor and set its key, begin a new transaction updating half the rows, prepare at timestamp 30, then invoke the scenario operation on the checkpoint cursor and expect `Invalid argument`.

State/persistence behavior: the checkpoint cursor has its own internal read transaction, but the session is in prepared state. The API must reject reads rather than mixing transaction contexts.

Dependencies/integration: prepared transactions, checkpoint cursor reads, timestamped updates, and disaggregated skip for checkpoint cursors.

Risks/test signals: operation matrix ensures all major read entry points fail consistently.
