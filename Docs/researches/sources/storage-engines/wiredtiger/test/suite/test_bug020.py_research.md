# sources/storage-engines/wiredtiger/test/suite/test_bug020.py

Purpose: verifies that an existing `WiredTiger.turtle.set` file can replace a missing `WiredTiger.turtle` file during open.

Important APIs/types/functions: `SimpleDataSet.populate`, `close_conn`, `open_conn`, `os.rename`, and `expectedStdoutPattern`.

Control flow: populate `table:bug020` with 1,000 rows, close the connection, rename `WiredTiger.turtle` to `WiredTiger.turtle.set`, and reopen while expecting stdout containing `WiredTiger.turtle not found`.

State/persistence behavior: manipulates the turtle metadata file after a clean close. The tested open path must recover/recognize the `.set` copy and continue.

Dependencies/integration: filesystem metadata handling, connection startup, and turtle file recovery logic.

Risks/test signals: no readback of table contents; the startup path itself is the signal. Message wording is part of the assertion.
