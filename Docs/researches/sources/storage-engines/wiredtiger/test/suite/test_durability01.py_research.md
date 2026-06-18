# sources/storage-engines/wiredtiger/test/suite/test_durability01.py

Purpose: checks metadata durability after exclusive operations such as verify close file handles and flush data files.

Important APIs and control flow: creates a table, then for 100 iterations writes one row, either checkpoints every fifth row or calls `verifyUntilSuccess` on other iterations, copies the live WiredTiger home to `RESTART`, opens the copy, verifies, and closes it.

State and persistence: the live copy simulates a crash snapshot. The test is looking for metadata checkpoints staying in sync with data files after verify-triggered file close.

Dependencies and integration: uses `copy_wiredtiger_home`, `suite_subprocess`, `setUpConnectionOpen`, `setUpSessionOpen`, and `verifyUntilSuccess`.

Risks and test signals: verification in copied homes must always succeed. Failures suggest metadata was not durably checkpointed while data files changed, creating restart inconsistency.
