# sources/storage-engines/wiredtiger/test/suite/test_prepare09.py

## Purpose

Validates rollback of prepared updates that were reconciled to disk does not leave incorrect tombstones or stale visibility metadata. It targets column and integer-row tables with large string values.

## Important APIs, Control Flow, and State

`test_prepare09` creates timestamped tables, pins oldest/stable to 1, and uses direct cursor assignment plus `prepare_transaction` and `rollback_transaction`. `test_prepared_update_is_aborted_correctly_with_on_disk_value` commits key 1 at timestamp 2, fills many other keys to force the value onto disk, prepares a replacement at timestamp 3, rolls it back, drives more page pressure, and asserts key 1 still returns the original value. `test_prepared_update_is_aborted_correctly` prepares inserts for keys 1 to 3 without a prior committed value, forces the prepare to disk through many additional writes, rolls it back, and asserts key 1 is not found.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger errors/constants, `wttest`, and scenario generation. The main risk is rollback accidentally inserting a tombstone where an older committed value should remain visible, or failing to hide an aborted insert. Strong signals are large values, low cache, post-rollback point searches, and `WT_NOTFOUND` checks.
