# sources/storage-engines/wiredtiger/test/suite/test_txn18.py

## Purpose
`test_txn18.py` verifies `log=(recover=error)` and `log=(recover=on)` behavior before and after recovery is required.

## Important APIs, Types, and Functions
The class defines `mkvalue` and `test_recovery`, scenarios for key format, configs `conn_recerror` and `conn_recon`, `helper.copy_wiredtiger_home`, `wiredtiger_open`, and transaction log recovery assertions.

## Control Flow
The test creates and checkpoints metadata for a logged table, writes 10,000 rows, copies the home to two directories, closes the original, verifies opening with `recover=error` fails while recovery is needed, opens with `recover=on`, validates all data, closes cleanly, then reopens with `recover=error`.

## State and Persistence Behavior
Copied homes represent crash states with unapplied logs. After recovery and clean shutdown, no recovery should be required.

## Dependencies and Integration Points
Depends on helper home copying, log recovery modes, and row/column key scenarios.

## Risks and Edge Cases
If metadata checkpointing is removed, create metadata may not be durable enough. Error message matching depends on "recovery must be run".

## Test Signals
`recover=error` fails before recovery, `recover=on` succeeds and data scans correctly, and `recover=error` succeeds after clean shutdown.
