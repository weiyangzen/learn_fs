# sources/storage-engines/wiredtiger/test/suite/test_hs16.py

## Purpose

Regression test that checkpointing does not panic when a no-timestamp update is inserted into history-store-related reconciliation state while another session pins visibility.

## Important APIs, Types, and Functions

Defines `test_hs16`, `create_key`, and one test across column/string row formats.

## Control Flow

It writes key 1 without timestamp, writes timestamped values at 1 and 2, opens another session with an active transaction to make a later no-timestamp update non-globally visible, applies that no-timestamp update, then checkpoints.

## State and Persistence Behavior

State is a mixed timestamp/no-timestamp chain with a second session holding a transaction. The expected behavior is simply successful checkpoint.

## Dependencies and Integration Points

Depends on small cache, scenario generation, transaction `no_timestamp=true`, multiple sessions, and checkpoint reconciliation.

## Risks and Maintenance Signals

There are no value or stat assertions; it is a no-crash regression. The code appears to set key 2 through `cursor` rather than `cursor2`, but its role is to keep session2 active.

## Test Signals

Signal is checkpoint completion without panic or exception.
