# sources/storage-engines/wiredtiger/test/suite/test_bug024.py

Purpose: regression for WT-6526: a readonly connection should open successfully if the database was stopped while a temporary turtle file existed.

Important APIs/types/functions: `SimpleDataSet`, `shutil.copy`, `wiredtiger_open`, `conn.close`, and hook skips for tiered and disaggregated storage.

Control flow: create and populate `table:test_bug024`, close the connection, copy `WiredTiger.turtle` to `WiredTiger.turtle.set`, open the home with `readonly`, then close it.

State/persistence behavior: simulates a home directory containing both stable turtle metadata and a temporary `.set` turtle file. Readonly startup must not require writing cleanup metadata and must not crash.

Dependencies/integration: connection startup, turtle file handling, readonly mode, and filesystem copy semantics.

Risks/test signals: no content assertion; pass condition is successful readonly open/close. Skipped where turtle manipulation is incompatible with storage architecture.
