# sources/storage-engines/pebble/internal/manifest/version_edit.go

## Purpose
`version_edit.go` defines the MANIFEST edit record format and the machinery for decoding, encoding, accumulating, and applying edits to produce new `Version` instances. It is the main bridge between durable manifest records and in-memory version state.

## Important APIs, Types, And Functions
- Disk-format constants include LevelDB, RocksDB, and Pebble tags for logs, files, range keys, backing tables, blob files, excise records, and compaction marks.
- `VersionEdit` holds comparer/log/file-number state, deleted and new tables, backing table additions/removals, blob file changes, excise operations, and tables marked for compaction.
- Entry types include `DeletedTableEntry`, `DeletedBlobFileEntry`, `NewTableEntry`, `TableMarkedForCompactionEntry`, and `ExciseOpEntry`.
- `Decode` and `Encode` implement binary manifest serialization.
- `DebugString`, `String`, and `ParseVersionEditDebug` support test/debug text representations.
- `BulkVersionEdit` accumulates one or more edits and `Apply` creates a new `Version`.

## Control Flow
`Decode` reads uvarint tags until EOF, dispatching each tag to field-specific parsing. New table tags handle old point-only encodings, range-key encodings with bound markers, creation time, virtual backing file numbers, synthetic prefix/suffix, and blob references. `Encode` chooses the narrowest compatible new-file tag and emits custom fields when needed. `Accumulate` cancels add/delete pairs, resolves decoded virtual table backings, updates blob additions/deletions, and carries compaction marks. `Apply` clones current version state, updates blob files, removes deleted tables, inserts added tables with read-compaction seek counts and blob reference resolution, maintains range-key indexes/regions, and validates local ordering around edits.

## State And Persistence Behavior
This file directly owns persistent manifest semantics. Some state is intentionally absent from persistence, such as compaction state and table refcounts, while comparer name, log numbers, file numbers, sequence number upper bounds, table bounds, virtual/backing metadata, blob files, excise records, and compaction marks are encoded. Decoded virtual tables require backing resolution during accumulation.

## Dependencies And Integration Points
It depends on `base`, table/blob metadata, level metadata, version construction, L0 organizer callers, record log readers/writers outside this file, `sstable` synthetic transforms, and invariant checks. It also carries compatibility behavior for LevelDB/RocksDB tags and column family rejection.

## Risks And Test Signals
Compatibility and data-loss risks are high. Important hazards include custom tag ignore rules, range-key bound marker correctness, virtual backing lifecycle, blob reference `BackingValueSize` preservation, add/delete accumulation cancellation, and ordering validation after apply. `version_edit_test.go` provides roundtrip, decode fixture, last-sequence compatibility, datadriven apply, and debug parse roundtrip coverage.
