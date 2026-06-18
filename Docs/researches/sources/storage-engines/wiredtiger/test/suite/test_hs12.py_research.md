# sources/storage-engines/wiredtiger/test/suite/test_hs12.py

## Purpose

Verifies reverse modifies that append or prepend string content remain visible to an older snapshot after later updates and eviction.

## Important APIs, Types, and Functions

Defines `test_hs12` with one test across column and integer row formats, using `wiredtiger.Modify` offsets beyond end and at start.

## Control Flow

It inserts two values, modifies key 1 by appending `A` at offset 130 and key 2 by prepending `AB`, confirms another session sees those values, starts a long transaction in that session, updates key 1 to a new value, evicts the page with `release_evict`, and checks the older session still sees the modified historical values.

## State and Persistence Behavior

State includes non-timestamped snapshots, reverse modify reconstruction, and eviction while an older transaction pins visibility.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, scenario key formats, multiple sessions, and debug eviction cursor behavior.

## Risks and Maintenance Signals

The declared `valuebig` is unused. The test focuses on one append and one prepend case, not broad offset coverage.

## Test Signals

Signals are older-snapshot values `value1 + A` and `AB + value1` after eviction.
