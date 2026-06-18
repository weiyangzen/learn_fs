<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/index.py -->
# sources/sync-backup/bup/lib/bup/index.py

## Purpose
This module implements bup's filesystem index format (`bupindex`) and metadata side store (`bupindex.meta`). It records stat data, metadata offsets, tree hierarchy, content hashes, and validity flags so `bup save` can avoid rehashing unchanged files.

## Important APIs, Types, And Functions
Important constants include `INDEX_HDR`, `INDEX_SIG`, `IX_EXISTS`, `IX_HASHVALID`, and `IX_SHAMISSING`. Core types are `MetaStoreReader`, `MetaStoreWriter`, `Entry`, `NewEntry`, `BlankNewEntry`, `ExistingEntry`, `Reader`, and `Writer`. Path helpers include `pathsplit()`, `unique_resolved_paths()`, `reduce_paths()`, and `merge()`.

## Control Flow
`Writer.add()` receives sorted paths, stat data, metadata offsets, and optional hash callbacks, converts paths to hierarchy elements, and uses `_golevel()`/`Level.write()` to close completed directory levels into a single mmap-friendly tree. `Reader` opens an existing index read-write, verifies the header, mmaps the file, reads the footer count, and materializes `ExistingEntry` objects on traversal. `ExistingEntry.repack()` writes modified flags back into the mmap and propagates invalidation to parents.

## State And Persistence Behavior
Index entries are binary records preceded by nul-terminated basenames and followed by a footer count. Metadata is append-only and deduplicated by encoded bytes in `MetaStoreWriter._offsets`. Index writes use `atomically_replaced_file` and fsync. Existing indexes are mutable through mmap, so flag changes can persist in place.

## Dependencies And Integration Points
It depends on `metadata.Metadata`, `xstat` nanosecond conversions, `_helpers.bytescmp`, mmap and atomic helpers. It is used by `cmd/index.py` and `cmd/save.py` to maintain scan state, by save logic to find valid hashes and metadata, and by hardlink tracking.

## Risks And Edge Cases
`Writer._add()` requires reverse-sorted path order and raises if order is wrong. `Reader` returns an empty reader for missing or invalid headers rather than always failing. Corrupt metadata can abort `MetaStoreWriter` initialization. Device checks, timestamp clamping (`tmax`), and fake entries affect stale detection. Direct mmap mutation means crashes around `save()` can leave partially updated flags.

## Test Signals
`test/int/test_index.py`, `test/ext/test-index`, `test/ext/test-index-clear`, `test/ext/test-index-save-type-change`, `test/ext/test-index-check-device`, `test/ext/test-rm-between-index-and-save`, and save/restore tests cover index construction, filtering, stale detection, metadata storage, type changes, device checks, and merge ordering.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/index.py -->
