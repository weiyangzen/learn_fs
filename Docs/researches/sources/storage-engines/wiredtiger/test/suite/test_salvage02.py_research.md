<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_salvage02.py

Purpose: validates startup with `salvage=true` after the history store file is removed, ensuring primary table data remains openable and readable after history-store loss.

Important APIs/types/functions: `test_salvage02` uses `SimpleDataSet`, timestamped transactions, `wiredtiger_strerror`, `WT_ROLLBACK`, `WiredTigerError`, and `make_scenarios` for row-integer and column key formats. `large_updates` writes each row in its own transaction and rolls back if a rollback error is surfaced.

Control flow: populate a table with 1000 rows, write value A at commit ts 1, pin oldest/stable at 1, write value B at commit ts 2 to create history store content, checkpoint, close the connection, delete `WiredTigerHS.wt`, reopen with `salvage=true`, and read the table.

State and persistence behavior: the key state transition is from a timestamped table with history store contents to a deliberately incomplete home directory. The test does not validate historical reads; it checks that salvage can reconstruct a usable current table view with the expected row count.

Dependencies/integration points: exercises history store file handling, salvage startup configuration, checkpoint durability, timestamp metadata, and dataset key formatting. Risks include assumptions about the history store filename and value visibility after salvage; the test signal is successful reopen plus exactly `nrows` records from `session.open_cursor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_salvage02.py -->
