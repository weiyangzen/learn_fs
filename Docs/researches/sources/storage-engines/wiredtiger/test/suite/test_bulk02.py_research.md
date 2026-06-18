# sources/storage-engines/wiredtiger/test/suite/test_bulk02.py

Purpose: tests bulk-load interactions with checkpoints, hot backup, and transactions.

Important APIs/types/functions: `suite_subprocess`, `simple_key`, `simple_value`, `make_scenarios`, checkpoint configs `name=myckpt` or unnamed, backup helper `backup`, and `assertRaisesWithMessage`.

Control flow: `test_bulkload_checkpoint` opens a bulk cursor, inserts records, checkpoints repeatedly while the cursor is open, closes it, and for named checkpoints verifies the skipped table cannot be opened from that checkpoint. `test_bulkload_backup` inserts via open bulk cursor, optionally checkpoints, runs backup from the same or different session, opens the backup, and confirms the object is empty. `test_bulk_checkpoint_in_txn` verifies opening a bulk cursor inside an active transaction fails with a clear message.

State/persistence behavior: open bulk-load handles are intentionally skipped by checkpoint/backup until closed. Bulk cursor state must not leak partial rows into durable snapshots or backup copies.

Dependencies/integration: checkpoint subsystem, backup tool wrapper, session/connection handle caches, transaction state validation, and file/table plus row/var scenarios.

Risks/test signals: failure indicates checkpoint/backup included unclosed bulk content or transaction restrictions regressed.
