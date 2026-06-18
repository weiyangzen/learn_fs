<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal.go -->
# sources/storage-engines/pebble/internal.go

## Purpose
This file re-exports selected internal Pebble primitives through the `pebble` package, mostly for tests, compatibility, and advanced callers that need file-format-visible key concepts.

## Important APIs, Types, And Functions
It aliases `SeqNum`, `InternalKeyKind`, `InternalKeyTrailer`, `InternalKey`, `KeyRange`, `internalIterator`, `topLevelIterator`, `AttributeAndLen`, `ShortAttribute`, `LazyFetcher`, and `CompressionCounters`. It exports internal key-kind constants, `MakeInternalKey`, `MakeInternalKeyTrailer`, `IsCorruptionError`, and deprecated `ErrCorruption`.

## Control Flow
There is no complex control flow: constructors delegate to `base.MakeInternalKey` and `base.MakeTrailer`, and corruption checks delegate to `base.IsCorruptionError`.

## State And Persistence Behavior
The constants are part of Pebble's file format and must remain stable. The aliases expose existing internal representations without storing state.

## Dependencies And Integration Points
The file integrates `internal/base` and `sstable/block` with the top-level Pebble package. Ingest, iterator, lazy-value, and corruption tests use these exported forms.

## Risks And Edge Cases
Changing constant values or alias semantics would be an on-disk compatibility break. `ErrCorruption` remains for compatibility but callers should prefer `IsCorruptionError`.

## Test Signals
Indirectly covered throughout Pebble tests that construct internal keys, key ranges, lazy values, compression counters, and corruption assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal.go -->
