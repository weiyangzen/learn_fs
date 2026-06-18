# sources/storage-engines/wiredtiger/test/suite/test_timestamp06.py

## Purpose
`test_timestamp06.py` verifies multistep transactions that set multiple commit timestamps before final commit, especially checkpoint and rollback behavior for logged versus non-logged timestamped tables.

## Important APIs, Types, and Functions
The class uses `copy_wiredtiger_home`, helpers `check`, `backup_check`, and `ckpt_backup`, plus scenarios for key format, checkpoint `use_timestamp`, and logging compatibility.

## Control Flow
The test creates a logged timestamp table and a non-logged timestamp table. In one transaction it sets commit timestamp 1 and writes value 1 for all keys, then timestamp 101 and writes value 2, then timestamp 201 and writes value 3, then commits at timestamp 301. It verifies latest reads, sets oldest 100 and stable 200, verifies logged tables see value 3 while non-logged tables see value 2 at stable, and checks backup contents depending on checkpoint timestamp mode. If the checkpoint used timestamps, it calls rollback-to-stable and verifies logged tables keep value 3 while non-logged tables roll back to value 2 for both timestamped and non-timestamped reads.

## State and Persistence Behavior
The same transaction contains multiple timestamped update phases, so the first and later commit timestamps must be recorded correctly for checkpoint and rollback selection.

## Dependencies and Integration Points
It integrates with timestamped transaction API, checkpoints, backup copies, logging, rollback-to-stable, and cursor verification.

## Risks and Test Signals
Risks include checkpointing the final update for non-logged tables despite stable being earlier or rollback using the wrong timestamp. Signals are backup value counts and post-rollback dictionaries.
