# sources/storage-engines/wiredtiger/test/suite/test_hazard.py

## Purpose

Stress-regression test for dynamic growth and cleanup of a session's hazard pointer array.

## Important APIs, Types, and Functions

Defines `test_hazard` with a single method that uses `SimpleDataSet` and many open cursors.

## Control Flow

It populates a 1000-row table, opens 10,000 cursors on the same session, positions each on key 10 to pin a page and allocate a hazard pointer, stores cursors, then closes them all.

## State and Persistence Behavior

State is in-memory hazard pointer allocation and release; data persistence is incidental through dataset population.

## Dependencies and Integration Points

Depends on `wttest`, `SimpleDataSet`, cursor search, and internal hazard pointer management.

## Risks and Maintenance Signals

The test has no explicit stat assertions; success is no crash, no allocation failure, and no teardown leak. It is a coarse stress signal.

## Test Signals

Signal is completion of massive cursor open/search/close cycle without errors.
