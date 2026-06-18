# sources/storage-engines/pebble/get.go

## Purpose
Implements the public point lookup API `DB.Get` and its shared internal helper. It performs a snapshot-consistent prefix seek through Pebble's iterator stack and returns a value slice whose lifetime is tied to the returned iterator closer.

## Important APIs, Types, And Functions
`DB.Get(key []byte) ([]byte, io.Closer, error)` delegates to `getInternal` with no batch or snapshot. `getInternal(key, b, s)` checks `d.closed`, selects a sequence number from the provided `Snapshot` or `visibleSeqNum`, builds an iterator with optional batch and `categoryGet`, uses `SeekPrefixGE`, compares the found key with `Comparer.Equal`, calls `ValueAndErr`, and returns the iterator as the `io.Closer`.

## Control Flow
The function panics if the DB is closed, constructs a read iterator at the desired snapshot sequence number, seeks to the key prefix, and treats a missing seek result or unequal key as `ErrNotFound` after closing the iterator. If value retrieval errors, it combines the value error with iterator close error. On success, it deliberately leaves the iterator open and returns it to the caller as the closer that pins the returned value bytes.

## State And Persistence Behavior
`Get` is read-only. It observes the current visible sequence number or a snapshot sequence number and may merge state from a batch, memtables, flushable ingests, and SSTables through `newIter`. The returned value slice is backed by iterator-owned resources, so caller closure is required to release memory/cache references.

## Dependencies And Integration Points
The code depends on `DB.newIter`, `Iterator.SeekPrefixGE`, `Iterator.Key`, `Iterator.ValueAndErr`, `Iterator.Close`, `Snapshot.seqNum`, `Batch`, `base.SeqNum`, comparer equality, `ErrNotFound`, and iterator category accounting. It is the simple public wrapper over the same read stack used by scans and internal lookups.

## Risks And Edge Cases
The main contract risk is leaking the returned closer, which pins iterator resources. Empty keys are valid and must flow through comparer/iterator logic, as covered by flush tests. Prefix seek must be followed by exact equality to avoid returning the next key. Error handling must close iterators on not-found and combine errors on failed value retrieval without closing on success.

## Test Signals
Direct and indirect signals include point lookup tests throughout the repository, `TestFlushEmptyKey`, snapshot and batch read tests, leak detection for unclosed iterators, and errors surfaced from iterator close or value retrieval.
