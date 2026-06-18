<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh

## Purpose

`XrdPfcFPurgeState.hh` declares the state object used to collect file purge candidates from the XrdPfc cache namespace.

## Important APIs, Types, And Functions

- `PurgeCandidate` stores a candidate path, block count, and timestamp.
- `list_t` holds unconditional candidates; `map_t` is a `std::multimap<time_t, PurgeCandidate>` for LRU ordering.
- Accessors expose candidate containers and block/byte totals.
- Threshold setters configure normal age and unverified-checksum retention ages.
- `CheckFile()`, `ProcessDirAndRecurse()`, and `TraverseNamespace()` perform candidate discovery.

## Control Flow

Callers construct the object with a requested byte count, optionally set age thresholds, traverse a namespace root, then consume `refList()` and `refMap()` for purge execution.

## State And Persistence

The class holds candidate state in memory and references the OSS. It does not itself persist changes in the active implementation.

## Dependencies And Integration Points

It forward-declares `XrdOss`, `Info`, and `FsTraversal`, and uses standard list/map/string/stat types. It is part of the cache purge subsystem.

## Risks And Edge Cases

- Exposing mutable references to internal containers lets callers break invariants.
- Timestamp multimap allows duplicate times, which is intended but means deterministic tie order depends on insertion order only indirectly.
- Requested bytes are rounded to blocks with `(bytes >> 9) + 1`, so exact multiples request one extra block.

## Test Signals

Tests should validate constructor rounding, accessor totals, threshold setters, mutable container behavior, and integration with traversal fake data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFPurgeState.hh -->
