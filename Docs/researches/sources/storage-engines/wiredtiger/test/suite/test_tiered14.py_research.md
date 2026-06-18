# sources/storage-engines/wiredtiger/test/suite/test_tiered14.py

## Purpose
`test_tiered14.py` is a randomized tiered-storage workflow test covering arbitrary sequences of data additions, updates, checkpoints, flushes, restarts, and validation.

## Important APIs, Types, and Functions
The class uses `TrackedSimpleDataSet` and optionally `TrackedComplexDataSet` with scenario dimensions for key format, value-size multiplier, dataset type, and storage source. `playback(testnum, ops)` is the core interpreter for operation strings, and `progress` annotates failures with test number and position.

## Control Flow
Each playback creates a unique table URI, populates it, then interprets operations: `a` stores a random range of new keys, `u` updates a random existing range, `c` checkpoints, `r` reopens the connection, `f` flushes tier, and `.` checks the tracked dataset. `test_tiered` runs a fixed sequence, then 10 data-heavy random sequences, then 10 sequences with more operational churn, using `random.seed(0)` for repeatability.

## State and Persistence Behavior
Tracked datasets maintain expected logical contents across local cache, on-disk files, shared tier objects, checkpoints, and restarts. Unique URIs avoid cleanup complexity between randomized runs.

## Dependencies and Integration Points
It integrates with `wtdataset` tracked datasets, tiered flush, reopen behavior, random workload generation, and scenario pruning through the helper configuration.

## Risks and Test Signals
Risks include rare operation-order bugs in tiered metadata and object visibility. The signal is that every inserted/updated expected value survives validation at checkpoints, after flushes, and after reopens.
