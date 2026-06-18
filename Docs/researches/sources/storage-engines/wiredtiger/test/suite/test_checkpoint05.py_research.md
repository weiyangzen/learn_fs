# sources/storage-engines/wiredtiger/test/suite/test_checkpoint05.py

Purpose: ensures WiredTiger does not accumulate many checkpoints while a backup cursor is open; checkpoints created after backup start should still be deleted as usual.

Important APIs/types/functions: metadata cursor `metadata:`, helper `count_checkpoints`, backup cursor `open_cursor('backup:')`, forced checkpoints, logging config with `remove=false`, and precise/fuzzy scenarios.

Control flow: create a table, insert 16 rows, checkpoint, open a backup cursor, count checkpoint strings in metadata, sleep 2 seconds to avoid immediate pinning effects, force 50 checkpoints, count metadata checkpoint references again, and assert the final count is less than three times the initial count.

State/persistence behavior: backup cursor pins a checkpoint, but later internal checkpoints should not accumulate unbounded metadata entries.

Dependencies/integration: backup cursor pinning, checkpoint deletion/metadata cleanup, logging, and precise checkpoint stable timestamp setup.

Risks/test signals: threshold is intentionally generous. Failure indicates checkpoint cleanup was blocked too broadly by the backup cursor.
