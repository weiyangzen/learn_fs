# sources/storage-engines/leveldb/db/db_iter.cc

## Purpose
This file implements `DBIter`, the user-facing iterator adapter that turns internal `(user key, sequence, value type)` entries from memtables and tables into visible user key/value entries at a snapshot sequence.

## Important APIs, Types, And Functions
The anonymous `DBIter` class derives from `Iterator` and implements `Valid`, `key`, `value`, `status`, `Next`, `Prev`, `Seek`, `SeekToFirst`, and `SeekToLast`. Private helpers `FindNextUserEntry`, `FindPrevUserEntry`, `ParseKey`, `SaveKey`, `ClearSavedValue`, and `RandomCompactionPeriod` manage visibility, direction switching, saved reverse values, and read sampling. `NewDBIterator` is the exported factory.

## Control Flow
Forward iteration skips entries newer than the snapshot, hides older values behind deletion markers, and returns the first visible value for a user key. Reverse iteration walks internal entries backwards, retaining the latest visible non-deleted value for each previous user key. Direction changes reposition the child iterator to avoid re-yielding the current user key. Seek constructs an internal seek key with `kValueTypeForSeek`.

## State And Persistence Behavior
The iterator has no durable state, but it affects compaction scheduling through `DBImpl::RecordReadSample` after roughly randomized `config::kReadBytesPeriod` bytes. It preserves snapshot state via the fixed `sequence_`. Large saved reverse values may release capacity to avoid retaining excessive memory.

## Dependencies And Integration Points
It depends on `DBImpl`, internal key parsing, `Iterator`, `Random`, comparators, logging utilities, and config constants. `DBImpl::NewIterator` wraps a merging internal iterator with this adapter.

## Risks And Edge Cases
Iterator correctness hinges on internal-key ordering by user key then decreasing sequence. Direction switching around invalid child positions, deletion markers, corrupted internal keys, and saved large values are sensitive paths. Read sampling must not corrupt iteration state.

## Test Signals
`db_test.cc` iterator tests cover empty/single/multi-key scans, seek boundaries, forward/reverse direction changes, deletes, compaction, snapshot pinning, large values, and randomized model comparison.
