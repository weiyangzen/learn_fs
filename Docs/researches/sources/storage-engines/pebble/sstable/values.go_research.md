# sources/storage-engines/pebble/sstable/values.go

## Purpose
Defines how SSTable iterators construct `base.InternalValue` instances from encoded value prefixes and handles, including in-place values, value-block handles, and external blob handles.

## Important APIs, Types, And Functions
`AssertNoBlobHandles`, `DebugHandlesBlobContext`, `LoadValBlobContext`, `BlobReferences`, `TableBlobContext`, and `defaultInternalValueConstructor.GetInternalValueForPrefixAndValueHandle` are key APIs. The constructor embeds blob context, read env, `valblk.Reader`, and a reusable lazy fetcher.

## Control Flow
If the value prefix indicates a value-block handle, the method delegates to `valblk.Reader`. If it indicates a blob handle, it decodes the inline handle preface, optionally returns a debug representation, resolves blob reference IDs to file IDs, sets lazy-fetcher metadata and stats, and returns a `LazyValue` carrying the handle suffix.

## State And Persistence Behavior
Persistent state is encoded in SSTable value bytes and blob reference metadata. Runtime state includes lazy fetchers, blob contexts, and iterator stats. `LoadValBlobContext` creates a blob `ValueFetcher` that the caller must close.

## Dependencies And Integration Points
Integrates SSTable block iterators with value-block reader, blob reader/provider code, `base.LazyValue`, iterator stats, and manifest blob references.

## Risks And Edge Cases
Missing blob references cause assertion panics unless a debug handle function is installed. `AssertNoBlobHandles` intentionally panics on unexpected external blobs. Lazy fetcher reuse means returned internal values must respect documented lifetimes or be cloned.

## Test Signals
Covered by SSTable/blob/value-block tests and debug formatting paths. Runtime stats for separated point values indicate construction/fetch behavior.
