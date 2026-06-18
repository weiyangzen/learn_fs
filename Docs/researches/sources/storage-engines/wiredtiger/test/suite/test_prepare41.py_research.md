# sources/storage-engines/wiredtiger/test/suite/test_prepare41.py

## Purpose

Tests that update restore for rolled-back prepared operations retains full updates needed to reconstruct modifies.

## Important APIs, Control Flow, and State

Both tests insert a 100-character value, apply a committed modify at timestamp 25 changing the first byte to `b`, then create a prepared operation at timestamp 30: either another modify changing the first byte to `d` or a delete. The prepared operation is rolled back at timestamp 35, pages are force-evicted with `ignore_prepare=true`, stable advances to 40, and checkpoint reinserts updates into the history store. A timestamp-25 read must reconstruct `b` plus 99 `a` characters in both cases.

## Dependencies, Risks, and Test Signals

Dependencies are `wiredtiger.Modify`, preserve-prepared configuration, release eviction page debug, checkpoint, and timestamped reads. The risk is update restore retaining a delta without the full base update after prepared rollback. Signals are exact reconstructed value comparisons.
