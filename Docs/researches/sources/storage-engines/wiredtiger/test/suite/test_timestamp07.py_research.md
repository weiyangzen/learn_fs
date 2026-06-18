# sources/storage-engines/wiredtiger/test/suite/test_timestamp07.py

## Purpose
`test_timestamp07.py` validates timestamped checkpoint and backup behavior for a non-logged timestamped table alongside a logged non-timestamped table, with file/table and row/column scenarios.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, binary string values, `check`, `check_reads`, `backup_check`, `ckpt_backup`, and `check_stable`. Scenarios vary key format, URI type, logging config, and key count.

## Control Flow
The test creates a non-logged timestamped table and a logged non-timestamped table. It inserts initial values at timestamps 1..n and verifies point reads at each timestamp. It advances oldest/stable to `nkeys`, updates both tables to value2 at timestamps `n+key`, and verifies a timestamped checkpoint/backup at stable excludes value2 from the non-logged table but includes it for the logged table. After advancing stable to `2*nkeys`, it verifies value2 appears everywhere. It then writes value3 at later timestamps, flushes logs without checkpoint, and verifies backup/checkpoint visibility remains stable for non-logged data while logged data appears.

## State and Persistence Behavior
Backups from copied WT homes are the persistence oracle. Stable timestamp controls non-logged timestamped data; logging controls the non-timestamped table.

## Dependencies and Integration Points
It integrates with checkpoint `use_timestamp=true`, log flush, backup copying, timestamped reads, and URI/key-format scenario coverage.

## Risks and Test Signals
Risks include checkpointing unstable non-logged updates or missing logged updates. Signals are exact value counts in live reads and copied backups.
