# sources/storage-engines/wiredtiger/test/suite/test_ovfl01.py

## Purpose
Regression test that bulk insert with overflow keys does not leave orphaned overflow items when reconciliation page split writes fail.

## APIs, Types, And Functions
Defines `test_ovfl01` with small leaf key/value limits, `timing_stress_for_test=(failpoint_rec_split_write)`, bulk cursor insertion, `Connection.reconfigure`, `Session.checkpoint`, and `Session.verify`.

## Control Flow, State, And Persistence
The test creates a string-key table where 1KB keys and values exceed overflow thresholds, bulk inserts 10,000 sorted records, tolerates `EBUSY` insert failures from the failpoint, disables the failpoint before closing the cursor, checkpoints, and verifies on-disk contents. Overflow pages and split state are persisted through reconciliation.

## Dependencies, Integration, Risks, And Test Signals
Depends on overflow key/value handling, bulk load, reconciliation split failpoint, and verify. Risks are orphaned overflow keys after partial split failures or unexpected errors other than `EBUSY`. Signals are successful checkpoint and `session.verify`, with expected stdout pattern ignored if the failpoint fires.
