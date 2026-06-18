# sources/storage-engines/wiredtiger/test/suite/test_hs09.py

## Purpose

Inspects checkpoint images to ensure the newest committed version is written to the data store and the second-newest committed version is written to the history store, excluding uncommitted/prepared updates.

## Important APIs, Types, and Functions

Defines `check_ckpt_hs`, which opens checkpoint cursors on the user table and `file:WiredTigerHS.wt`, and tests uncommitted, prepared, newest-version, and deleted-version cases.

## Control Flow

Each test writes timestamped versions, optionally leaves an uncommitted or prepared update on top, checkpoints, then scans the checkpoint data file and history store. HS tuples are checked for update type, value bytes, start timestamp, and stop timestamp.

## State and Persistence Behavior

State includes checkpoint-visible data-store records and raw HS table entries. Prepared updates use `ignore_prepare` semantics on checkpoint cursors.

## Dependencies and Integration Points

Depends on direct `WiredTigerHS.wt` cursor schema, scenario key formats, prepared transaction APIs, and checkpoint cursor behavior.

## Risks and Maintenance Signals

Direct HS tuple layout and update type numeric constants are internal and fragile. The delete test uses expected data value `0` as a sentinel to avoid comparing removed rows.

## Test Signals

Signals are checkpoint data values, HS standard update values and timestamps, absence of tombstone/birthmark update types, and exclusion of uncommitted/prepared top updates.
