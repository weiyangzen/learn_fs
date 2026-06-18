# sources/storage-engines/wiredtiger/test/suite/test_bug032.py

Purpose: regression for WT-11845, ensuring fast truncate does not rely only on aggregated page transaction state when the page contains updates invisible to the truncate transaction.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `conn.open_session`, transactions in multiple sessions, debug eviction cursor `debug=(release_evict)`, and `truncate_session.truncate`.

Control flow: populate a table with 500 large values on 10KB leaf pages, remove the target key, start `txn1` inserting the key but leave it uncommitted, commit `txn2` on a neighboring key, start the truncate transaction so its snapshot sees `txn2` but not `txn1`, commit `txn1`, evict the page to disk, truncate the whole table, commit the truncate, and verify the `txn1` key still exists.

State/persistence behavior: page aggregate transaction metadata can look visible because of `txn2`, but per-key visibility must prevent fast truncating the page containing `txn1`.

Dependencies/integration: snapshot isolation, fast truncate page selection, eviction, row/column key formats, and dataset page sizing.

Risks/test signals: failure is missing target key after truncate. The scenario is carefully staged so the insert is not converted into a visible modify.
