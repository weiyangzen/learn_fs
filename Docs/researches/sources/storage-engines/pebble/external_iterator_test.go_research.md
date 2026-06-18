# sources/storage-engines/pebble/external_iterator_test.go

## Purpose
Tests and benchmarks `NewExternalIter` over standalone SSTables, including initialization failures and scan performance.

## Important APIs, Types, And Functions
`TestExternalIterator` builds SSTables in an in-memory FS and iterates them with optional bounds, mask suffixes, and file lists. `testExternalIteratorInitError` wraps files in `flakyFile` to force intermittent `ReadAt` failures. `BenchmarkExternalIter_NonOverlapping_Scan` measures scan throughput over varying key and file counts.

## Control Flow
Datadriven commands reset the FS, build SSTables, run initialization-error loops, or create an external iterator and feed it to shared iterator test helpers. The flaky test retries many constructor calls, requiring either a surfaced `"flaky file"` error or a successfully closable iterator. The benchmark builds sorted SSTables, repeatedly opens file handles, constructs an iterator, and scans with `NextPrefix`.

## State And Persistence Behavior
All state is temporary in-memory SSTables and opened file handles. No DB manifest is used. Blob test values may be used while building to validate unsupported blob-reference behavior.

## Dependencies And Integration Points
Uses `datadriven`, `testkeys`, `sstable`, `objstorageprovider`, `blobtest`, `vfs`, and shared build/iterator helpers from Pebble tests. It directly validates `external_iterator.go`.

## Risks And Edge Cases
The most important edge case is constructor cleanup when reader initialization fails after some files have opened. Other covered areas include range-key masking, lower/upper bounds, unsupported blob values, and correct ordering across multiple external files.

## Test Signals
Signals are datadriven iterator output, expected constructor errors, absence of panics during flaky initialization, and benchmark key-count validation.
