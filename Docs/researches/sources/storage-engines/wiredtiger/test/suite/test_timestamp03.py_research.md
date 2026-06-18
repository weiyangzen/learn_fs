# sources/storage-engines/wiredtiger/test/suite/test_timestamp03.py

## Purpose
`test_timestamp03.py` validates timestamped checkpoint behavior across logged and non-logged objects, plus metadata logging flags for data files and the history store.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, `suite_subprocess`, `make_scenarios`, metadata cursors, `check`, `backup_check`, and `ckpt_backup`. Scenarios vary URI type, key format, checkpoint `use_timestamp` setting, and log compatibility configuration.

## Control Flow
The test creates four tables: timestamped logged, timestamped non-logged, non-timestamped logged, and non-timestamped non-logged. It inserts timestamped and non-timestamped values, verifies reads at many timestamps, advances oldest/stable, updates all tables, tests rounded reads before oldest, and checks timestamped checkpoint backups for old/new values according to `use_timestamp`. After advancing stable, it checks that backups include newer values. It then writes a third value, flushes the log without checkpoint, and verifies backup visibility differences between logged and non-logged tables. Finally it verifies metadata `log=(enabled=...)` values, including history store logging disabled.

## State and Persistence Behavior
It distinguishes log durability from checkpoint durability and timestamped checkpoint selection. Backup copies are the persistence oracle.

## Dependencies and Integration Points
It integrates with checkpoints, log flush, backup copy helpers, metadata, history store metadata, logging compatibility, and timestamp MVCC.

## Risks and Test Signals
Risks include recovering the wrong logged record, checkpointing unstable updates, or wrong metadata logging flags. Signals are backup value counts and metadata substring checks.
