# sources/storage-engines/wiredtiger/test/suite/test_bug014.py

Purpose: regression for WT-2115, where fast-delete pages could be incorrectly lost after a crash with an uncommitted truncate. It covers both column-store and row-string scenarios.

Important APIs/types/functions: `SimpleDataSet`, `make_scenarios`, `copy_wiredtiger_home`, `session.truncate`, separate checkpoint session, `setUpConnectionOpen`, and `setUpSessionOpen`.

Control flow: populate 1,000 rows on small pages, reopen to permit fast-delete, begin a transaction, truncate keys 250 through 500, checkpoint from another session while the truncate is uncommitted, copy the home directory as a simulated crash image, open the copy, and verify all 1,000 records still exist.

State/persistence behavior: the key state is an uncommitted fast-truncate visible to checkpoint processing but not durable committed data. The recovery image must not persist the logical deletion.

Dependencies/integration: exercises transaction visibility, checkpointing, fast truncate, copied-home crash simulation, and dataset key abstraction.

Risks/test signals: failure appears as missing records after opening `RESTART`; it is skipped only implicitly by scenario availability, not by hooks.
