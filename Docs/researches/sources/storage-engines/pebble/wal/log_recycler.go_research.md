<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler.go -->
# sources/storage-engines/pebble/wal/log_recycler.go

## Purpose
Maintains a bounded FIFO set of obsolete WAL files that may be reused instead of deleted. Recycling improves WAL creation/sync performance by avoiding some filesystem metadata work.

## Important APIs, Types, and Functions
`LogRecycler` stores a limit, minimum recyclable log number, queued `base.FileInfo` entries, and max log number seen. `Init`, `RatchetMinRecycleLogNum`, `Add`, `Peek`, `Stats`, `Pop`, `LogNumsForTesting`, and `maxLogNumForTesting` are the main methods.

## Control Flow
`Init` sets the queue limit. `RatchetMinRecycleLogNum` monotonically increases the minimum accepted file number. `Add` rejects logs below the minimum, ignores already-considered log numbers, updates `maxLogNum`, and appends if under the limit. `Peek` returns the head entry. `Pop` requires the requested file number to match the head, then removes it. `Stats` sums current queued sizes.

## State and Persistence Behavior
State is in memory only. The actual filesystem rename/reuse happens in the WAL manager's `logCreator`; this type only decides which obsolete files are eligible and in which order.

## Dependencies and Integration Points
Used by standalone and failover WAL managers to recycle safe obsolete WALs. It stores `base.FileInfo` so callers can reuse file numbers and sizes. Failover mode protects `Peek`/`Pop` pairs with an additional mutex because async segment creation can race.

## Risks and Edge Cases
Once a file number is considered and rejected due to queue limit, later `Add` for that number returns true without enqueuing because `maxLogNum` already advanced; callers must not delete such a file twice. `Pop` enforces FIFO head matching, so callers must coordinate `Peek` and `Pop` correctly.

## Test Signals
`log_recycler_test.go` covers min-number filtering, limit behavior, duplicate/previously considered numbers, stats-visible queue order, invalid pop errors, and empty pop errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler.go -->
