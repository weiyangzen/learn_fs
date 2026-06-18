# sources/storage-engines/wiredtiger/test/suite/test_bug022.py

Purpose: ensures modifies are not allowed on top of tombstone updates. It covers row-string and record-number column-store key formats.

Important APIs/types/functions: `wiredtiger.Modify`, `wiredtiger.WT_NOTFOUND`, `make_scenarios`, timestamp APIs, cursor `remove`, `modify`, and `search`.

Control flow: create a file object, set oldest timestamp to 1, insert 9,999 500-byte values at timestamp 2, remove every key at timestamp 3, checkpoint, then for every key attempt `cursor.modify([Modify('B', 0, 100)])` and assert `WT_NOTFOUND`, rolling back each attempted transaction. Finally search every key and assert `WT_NOTFOUND`.

State/persistence behavior: creates on-page tombstones through checkpointing and validates that modify does not resurrect or layer onto deleted versions.

Dependencies/integration: timestamped update chains, checkpoint reconciliation, row/column key abstraction, and modify semantics.

Risks/test signals: high row count for coverage; failures show as successful modify on deleted keys or visible records after tombstone.
