<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler_test.go -->
# sources/storage-engines/pebble/wal/log_recycler_test.go

## Purpose
Tests `LogRecycler` queue admission, ordering, duplicate handling, and pop validation.

## Important APIs, Types, and Functions
`TestLogRecycler` constructs a recycler with limit 3 and min recyclable log 4, then exercises `Add`, `Peek`, `Pop`, `LogNumsForTesting`, and `maxLogNumForTesting`.

## Control Flow
The test rejects logs below the minimum, adds logs up to the limit, verifies the queue and max number, rejects a past-limit log while advancing max, confirms re-adding an already considered log leaves state unchanged, checks invalid pop errors, pops in order, verifies a previously considered log is not newly recycled, then drains the queue and checks empty pop error text.

## State and Persistence Behavior
All state is in-memory recycler metadata; no files are created.

## Dependencies and Integration Points
Covers `log_recycler.go` and `base.FileInfo`/`DiskFileNum` formatting. It protects behavior expected by WAL manager recycling paths.

## Risks and Edge Cases
The test uses zero file sizes, so `Stats` size accumulation is not directly asserted. It focuses on queue membership and ordering.

## Test Signals
Passing confirms the recycler's bounded FIFO and max-number semantics are stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler_test.go -->
