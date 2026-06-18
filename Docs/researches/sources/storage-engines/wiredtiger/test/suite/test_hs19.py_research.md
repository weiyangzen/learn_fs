# sources/storage-engines/wiredtiger/test/suite/test_hs19.py

## Purpose

Regression test for reconstructing historical modify chains when a newer modify could otherwise be incorrectly used as the base during history-store rewrite/eviction.

## Important APIs, Types, and Functions

Defines `test_hs19`, `create_key`, and one scenario across column/string row formats.

## Control Flow

It starts with a no-timestamp base, applies modifies at timestamps 2 and 3, pins reconciliation state with another session, adds a large append modify at 4, a selected on-disk modify at 5, checkpoints, adds another modify at 6, evicts the page, then reads at timestamps 2, 3, and 4.

## State and Persistence Behavior

State includes a sequence of modifies in HS/data-store, a pinned transaction on a junk table, stable/oldest at 1, and eviction of a dirty page after checkpoint.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario generation, checkpoint `use_timestamp=true`, debug eviction, and multi-session timing.

## Risks and Maintenance Signals

The expected timestamp 4 reconstruction is manually assembled and includes append semantics that are easy to get wrong. It is a narrow but high-value corruption regression.

## Test Signals

Signals are exact reconstructed values at timestamps 2, 3, and 4 after checkpoint plus eviction.
