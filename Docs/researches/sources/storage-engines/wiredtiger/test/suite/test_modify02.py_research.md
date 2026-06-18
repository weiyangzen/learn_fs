# sources/storage-engines/wiredtiger/test/suite/test_modify02.py

## Purpose
Verifies that `Cursor.modify` fails when no base value exists for the target key.

## APIs, Types, And Functions
Defines `test_modify02` with value format scenarios `u` and `S`. It uses deterministic `random.Random(43)`, `modify_utils.create_mods`, `Cursor.modify`, and `wiredtiger.WT_NOTFOUND`.

## Control Flow, State, And Persistence
For 1000 generated cases, the test creates modify vectors but intentionally does not insert the old/base value into the table. Inside a transaction it sets only the key, calls `modify`, expects `WT_NOTFOUND`, and commits. No successful data modification should be persisted for those keys.

## Dependencies, Integration, Risks, And Test Signals
Depends on the modify API's requirement for an existing base value and on consistent generated modify vectors. Risks include accidentally creating values from deltas without a base or returning success for missing keys. The signal is exact `WT_NOTFOUND` for each attempted modify.
