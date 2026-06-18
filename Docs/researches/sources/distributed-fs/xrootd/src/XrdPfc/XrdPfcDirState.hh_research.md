<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh

## Purpose

`XrdPfcDirState.hh` declares the in-memory tree form of XrdPfc directory usage/statistics state and the `DataFsState` root manager.

## Important APIs, Types, And Functions

- `unlink_func` abstracts directory removal callbacks.
- Forward declarations link tree state with snapshot (`DirStateElement`, `DataFsSnapshot`) and purge (`DirPurgeElement`, `DataFsPurgeshot`) vector forms.
- `DirState` extends `DirStateBase` with here/recursive stats and usage, snapshot stats, parent pointer, child map, depth, and scanned flag.
- `DataFsState` extends `DataFsStateBase` with root node and stat reset timestamps.

## Control Flow

Resource monitor code finds or creates `DirState` nodes by LFN, records deltas in the relevant stats/usage fields, periodically calls `DataFsState::update_stats_and_usages()`, and resets interval or snapshot counters after reporting.

## State And Persistence

The header declares all in-memory directory state. Persistence occurs only when consumers export snapshots or when the update routine calls a supplied unlink function.

## Dependencies And Integration Points

It depends on `XrdPfcStats.hh`, `XrdPfcDirStateBase.hh`, `ctime`, `functional`, `map`, and `string`. `XrdPfcResourceMonitor` is the main integration point.

## Risks And Edge Cases

- Tree nodes are stored by value in `std::map`, so pointers to nodes remain stable only under map semantics and while nodes are not erased.
- Parent raw pointers require careful construction and no copying outside map-managed use.
- `m_scanned` state is public and cross-component code must update it consistently.

## Test Signals

Tests should validate declarations via resource monitor integration, pointer stability across child insertions, erase behavior during empty purge, and timestamp reset behavior on `DataFsState`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.hh -->
