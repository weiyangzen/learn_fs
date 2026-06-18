# sources/storage-engines/wiredtiger/test/suite/test_prepare27.py

## Purpose

Ensures an aborted prepared update is not chosen as the base value during rollback-to-stable reconstruction.

## Important APIs, Control Flow, and State

The test parameterizes column, integer-row, and string-row keys. It writes five timestamped values for one key, sets stable to 2, prepares a sixth value, evicts with `ignore_prepare=true` so the prepared update reaches the data store and older versions reach history store, rolls back the prepare, and calls `rollback_to_stable`. Comments document the expected chain as stable update 2 followed by aborted updates 6 and 5. It then opens a read transaction at timestamp 1 and searches the key, exercising retrieval of the earliest committed value rather than the aborted prepared base.

## Dependencies, Risks, and Test Signals

Dependencies are the transaction context manager, release eviction, `rollback_to_stable`, and scenario key conversion helpers. The risk is selecting an aborted prepared update as the restore base. The signal is successful post-RTS historical search without visibility corruption.
