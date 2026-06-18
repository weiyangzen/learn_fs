# sources/storage-engines/wiredtiger/test/suite/test_drop.py

Purpose: broad coverage for `WT_SESSION.drop` across files, simple tables, indexed tables, complex tables, cursors, transactions, reopen, and non-existent URIs.

Important APIs and control flow: scenarios cover `file:` and `table:`. Helper `drop` populates a dataset in a transaction, verifies open-cursor drop failure, verifies active-transaction EBUSY and rollback requirement, optionally reopens, chooses data or index URI, calls `dropUntilSuccess`, and confirms absence. `test_drop_dne` checks force succeeds on missing file/colgroup/index while non-force fails.

State and persistence: datasets may include indices and column groups. Reopen validates persisted state before drop.

Dependencies and integration: uses `SimpleDataSet`, `SimpleIndexDataSet`, `ComplexDataSet`, `confirm_does_not_exist`, `wiredtiger`, and skip for tiered storage.

Risks and test signals: catches incorrect busy handling, dirty transaction cleanup, dropped-index behavior, metadata removal, and force semantics.
