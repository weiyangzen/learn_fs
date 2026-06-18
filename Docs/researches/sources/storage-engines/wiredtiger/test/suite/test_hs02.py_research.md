# sources/storage-engines/wiredtiger/test/suite/test_hs02.py

## Purpose

Tests truncate visibility when history-store entries and timestamped updates coexist.

## Important APIs, Types, and Functions

Defines `large_updates`, a scanning `check` helper with expected value/count tuples, and scenarios for string-row and column-store key formats.

## Control Flow

It creates a main and extra table, writes one-third of rows at timestamp 1, pins oldest/stable, writes all rows at timestamp 100, forces pages out through updates to the extra table, truncates the first half of the main table at timestamp 200, then reads at timestamps 1, 100, and 200.

## State and Persistence Behavior

State includes timestamped row versions, history-store content pushed by cache pressure, and a range tombstone/truncate committed at a later timestamp.

## Dependencies and Integration Points

Depends on `SimpleDataSet`, `wttest`, scenario generation, timestamped transactions, and session truncate.

## Risks and Maintenance Signals

The `check` helper assumes scan order groups values exactly according to expected counts. It validates returned value runs more than individual key boundaries.

## Test Signals

Signals are full visibility at ts100, earlier value preservation at ts1, and half-table visibility after truncate at ts200.
