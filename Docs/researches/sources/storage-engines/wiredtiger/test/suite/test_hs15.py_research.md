# sources/storage-engines/wiredtiger/test/suite/test_hs15.py

## Purpose

Ensures eviction does not clear history-store content a second time after checkpoint has already handled an update without timestamp.

## Important APIs, Types, and Functions

Defines `test_hs15`, `create_key`, and a single timestamp/no-timestamp interaction workload across column and string row formats.

## Control Flow

The test inserts a no-timestamp base value, adds many timestamped rows for eviction pressure, modifies key 1 at timestamp 1, updates it at timestamp 2, advances oldest, checkpoints, then updates key 1 and many other keys at timestamp 3. It reads key 1 at timestamps 1, 2, and 3.

## State and Persistence Behavior

State includes a no-timestamp base update, timestamped modify/update records, checkpoint cleanup, and later eviction pressure that must not over-clear HS records.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, timestamp helpers, small cache, and scenario generation.

## Risks and Maintenance Signals

The test does not directly verify eviction happened; it relies on many inserts into a small cache. It is a specific regression sequence.

## Test Signals

Signals are exact values at timestamps 1, 2, and 3 after checkpoint and later pressure.
