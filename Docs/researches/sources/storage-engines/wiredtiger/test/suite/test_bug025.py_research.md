# sources/storage-engines/wiredtiger/test/suite/test_bug025.py

Purpose: regression for WT-7208: after a missing index file is accessed and returns an error, a later access through the same table cursor must not crash.

Important APIs/types/functions: `ComplexDataSet`, `ds.index_name`, `os.path.getsize`, `os.remove`, `expectedStderrPattern`, `open_conn`, and cursor item assignment.

Control flow: populate a complex table with an index, derive the `.wti` index filename, close the connection, remove the index file, reopen while allowing `No such file or directory` stderr, open the table cursor, attempt an insert twice while catching and printing exceptions, then close the cursor.

State/persistence behavior: intentionally corrupts the database by deleting an index file. The table/index handle error path must remain reusable and not leave a null pointer for the second access.

Dependencies/integration: complex dataset schema/index generation, lazy index file open, error capture, and table update propagation to indexes.

Risks/test signals: error location may vary, so the test only requires the missing-file diagnostic at least once. Core pass signal is absence of process crash.
