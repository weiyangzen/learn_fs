# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcStats.hh

## Purpose
Defines lightweight statistics containers for cache-file and directory-level accounting. `Stats` tracks IO/read/write/checksum counters; `DirStats` extends it with directory/file lifecycle and purge counters.

## Important APIs, Types, and Functions
- `Stats` fields: IO count, duration, bytes hit/missed/bypassed/written, `st_blocks` added, and checksum errors.
- `AddReadStats`, `AddBytesHit`, `AddWriteStats`, `IoAttach`, `IoDetach`, `BytesRead`, `BytesReadAndWritten`, `DeltaToReference`, `AddUp`, and `Reset`.
- `DirStats` adds removed blocks, opened/closed/created/removed file counts, and created/removed directory counts, with matching `DeltaToReference`, `AddUp`, and `Reset`.

## Control Flow
`File` accumulates `Stats` deltas and full stats, then reports them to `ResourceMonitor`. `ResourceMonitor` aggregates them into `DirState` and computes deltas/resets for reporting intervals.

## State and Persistence Behavior
The classes are plain in-memory counters. Their values are copied into `.cinfo` access records and directory snapshots by other code, but this header does not perform persistence.

## Dependencies and Integration Points
No external includes beyond namespace. Used by `File`, `Info`, `ResourceMonitor`, directory-state snapshots, and IO adapters.

## Risks and Test Signals
Risks include signed counter underflow in `DeltaToReference` if reference/current order is wrong, long-running counter overflow, and confusion between bytes and 512-byte `st_blocks`. Tests should cover add/reset/delta semantics and aggregation into access records.
