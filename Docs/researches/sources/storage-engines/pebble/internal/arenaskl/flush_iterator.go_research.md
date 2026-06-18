<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go -->
# sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go

## Purpose
This file defines the specialized memtable flush iterator for arena skiplists.

## Important APIs, Types, And Functions
`flushIterator` embeds `Iterator` and implements `base.InternalIterator`. `String`, `First`, and `Next` are implemented; `SeekGE`, `SeekPrefixGE`, `SeekLT`, `NextPrefix`, and `Prev` panic with assertion failures because flush code only performs forward full scans.

## Control Flow
`First` delegates to `Iterator.First`. `Next` mirrors `Iterator.Next` but omits bounds and prefix checks for the flush path, advancing level-zero links, decoding the key, and returning an in-place value.

## State And Persistence Behavior
It reads immutable skiplist nodes during flush and exposes in-place values. It does not mutate or persist state.

## Dependencies And Integration Points
It depends on `base.InternalIterator` and `errors.AssertionFailedf`. `Skiplist.NewFlushIter` constructs it for memtable flush code.

## Risks And Edge Cases
Because `Next` intentionally mirrors `Iterator.Next`, drift between the two implementations can introduce flush-only bugs. Unsupported operations panic, so callers must respect the restricted iterator contract.

## Test Signals
Coverage is indirect through skiplist iteration tests and Pebble flush/ingest tests that flush memtables.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/arenaskl/flush_iterator.go -->
