# sources/storage-engines/pebble/flushable.go

## Purpose
Defines the flushable abstraction used by immutable memtables and flushable ingests, plus the concrete `ingestedFlushable` wrapper that makes already-on-disk ingested SSTables visible in the memtable queue before they are placed in the LSM. It also provides overlap-detection helpers and a combined blob-file mapping spanning the current version and pending flushable ingests.

## Important APIs, Types, And Functions
`flushable` requires point, flush, range deletion, and range key iterators; range-key presence; byte accounting; readiness; and cheap overlap checks. `flushableEntry` adds queue metadata: `flushed`, forced-flush flags, WAL/log numbers, log sequence number, reader refs, memory release, file unrefs, and deletion callbacks. `readerRef`, `readerUnref`, and `readerUnrefLocked` manage lifecycle. `ingestedFlushable` stores ordered table metadata, comparer, iterator constructors, immutable level slice, excise span/sequence number, and blob file map. Key methods include `newIterInternal`, `newItersV2`, `newRangeDelIter`, `newRangeKeyIter`, `containsRangeKeys`, `readyForFlush`, `computePossibleOverlaps`, `anyFileOverlaps`, `determineOverlapAllIters`, `determineOverlapPointIterator`, `determineOverlapKeyspanIterator`, and `combinedBlobFileMapping.Lookup`.

## Control Flow
Flushable queue consumers call iterator methods to merge memtables and pending ingests into read state. `newIngestedFlushable` verifies file non-overlap under invariants, converts virtual metadata to physical metadata for file access, builds a key-sorted `LevelSlice`, detects range-key presence, and records blob mappings. Point reads use a level iterator over the flushable-ingest layer. Range deletion and range key reads construct keyspan level iterators and optionally merge synthetic excise tombstones/deletes. Overlap checks for ingested files use metadata bounds only, deliberately avoiding I/O; generic overlap checks for in-memory flushables use iterators and panic if an infallible iterator errors.

## State And Persistence Behavior
`flushable.go` itself persists nothing, but its data structures mediate durability. `flushableEntry.logNum`, `logSize`, and `logSeqNum` connect queue entries to WAL lifecycle. Reader refs defer memory accounting release and table/blob unrefs until no read state or queue reference remains. `ingestedFlushable` represents SSTables already linked or attached to storage, with sequence numbers persisted later through a version edit when flushed. Excise spans are surfaced as synthetic range deletion/range-key delete entries so reads observe destructive excise semantics before manifest placement.

## Dependencies And Integration Points
The file integrates with `manifest.TableMetadata`, `manifest.LevelSlice`, `newLevelIter`, `iterv2`, `keyspanimpl.LevelIter`, `MergingIter`, `base.UserKeyBounds`, `KeyRange`, blob file metadata, DB read state, ingest handling, flush scheduling, obsolete-file cleanup, and table/blob file reference counting. `combinedBlobFileMapping` is used by blob value fetching when blob references may point to current-version blob files or pending ingested flushables.

## Risks And Edge Cases
Reference count mistakes can leak memory/files or delete files still visible to readers. `ingestedFlushable.newFlushIter` intentionally panics because ingested files are already on disk; callers must not treat it like a memtable. Excise spans must be copied and merged correctly into range deletion and range key iterators. Metadata-only overlap checks may produce false positives, which is acceptable for safety but affects ingest placement and flushing. Blob-file lookup must search pending flushables or reads of newly ingested blob values may fail before manifest application.

## Test Signals
Signals come from `flushable_test.go`, ingest tests, read-state tests, and file-cache/reference leak tests. Useful symptoms include correct datadriven point/range-key/range-delete output from ingested flushables, expected `readyForFlush`/`containsRangeKeys` values, absence of reference-count panics, and successful blob value reads during flushable ingest windows.
