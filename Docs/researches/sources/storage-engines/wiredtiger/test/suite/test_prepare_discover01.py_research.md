# sources/storage-engines/wiredtiger/test/suite/test_prepare_discover01.py

Purpose: tests that a pending prepared transaction persisted in a checkpoint/backup can be discovered after reopening and rolled back through `prepared_discover:`.

Important APIs and types: `suite_subprocess.backup`, `wiredtiger_open`, `prepared_discover:` cursor, `claim_prepared_id`, `rollback_transaction(rollback_timestamp=...)`, timestamp setters, and `prepared_id_str`.

Control flow: it creates committed keys at timestamp 60, prepares keys 3-5 at timestamp 100 with prepared id 123, advances stable to 150, checkpoints, and backs up the home. The backup is opened with `precise_checkpoint=true,preserve_prepared=true`; a prepared-discover cursor is walked, the id is claimed, and the transaction is rolled back at timestamp 200.

State and persistence behavior: the key feature is preserving prepared artifacts in the backup checkpoint and resolving them in the reopened copy. Rolling back should remove the prepared inserts while leaving timestamp-60 data intact.

Dependencies and integration points: integrates backup copying, recovery/open, prepared transaction metadata, and discover-cursor iteration. The scenario matrix only includes row-store integer keys and a commit-ended setup.

Risks: the discovered key is asserted as integer 123, so `prepared_id_str` and cursor key encoding must stay consistent. Failure to claim before close would violate discover cursor protocol.

Test signals: exactly one prepared id is discovered and rollback completes without error.
