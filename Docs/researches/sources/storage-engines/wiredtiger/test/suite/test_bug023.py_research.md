# sources/storage-engines/wiredtiger/test/suite/test_bug023.py

Purpose: regression for WT-5930: a failed `wiredtiger_open` of a backup due to compatibility mismatch must not corrupt the backup so that a later correct open loses data.

Important APIs/types/functions: `backup_base`, `take_full_backup`, `wiredtiger_open`, `wiredtiger.WiredTigerError`, compatibility configs `release=3.2.0`, `require_min=3.2.0`, and `require_min=3.3.0`.

Control flow: create a logged file with compatibility 3.2, write/checkpoint 10 entries, write 10 more entries after the checkpoint, record original cursor data, take a full backup, close the original connection, intentionally open the backup with `require_min=3.3.0` expecting `/Version incompatibility detected:/`, then reopen with `require_min=3.2.0` and compare backup data to original data.

State/persistence behavior: tests backup recovery of post-checkpoint logged updates after a failed compatibility open. The failed startup must not leave metadata/log state partially advanced.

Dependencies/integration: backup harness, logging, compatibility gating, startup recovery, and data comparison.

Risks/test signals: only small data volume, but specifically targets a startup state transition after an expected open failure.
