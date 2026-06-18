# sources/user-network-fs/gcsfuse/internal/storage/fake/bucket.go

## Purpose
`fake/bucket.go` implements an in-memory `gcs.Bucket` for tests. It models object metadata, object contents, generation and metageneration checks, listing semantics, compose/copy/update/delete/move operations, HNS folder entries, appendable writes, readers, and multi-range downloaders without contacting GCS.

## Important APIs, Types, and Functions
`NewFakeBucket(clock, name, bucketType)` returns a `gcs.Bucket` backed by `bucket`. Internal types include `fakeObject`, sorted `fakeObjectSlice`, sorted `fakeFolderSlice`, and `bucket`. Helper methods perform name validation, prefix searching, object minting, folder minting, object copying, min-object conversion, precondition checking, and create/update insertion.

Public bucket methods include `Name`, `BucketType`, `ListObjects`, `NewReaderWithReadHandle`, `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, `FlushPendingWrites`, `FinalizeUpload`, `CopyObject`, `ComposeObjects`, `StatObject`, `UpdateObject`, `DeleteObject`, `MoveObject`, folder CRUD/rename, `NewMultiRangeDownloader`, and `GCSName`.

## Control Flow
Object creation validates names, reads request contents, validates CRC32C/MD5 and generation/metageneration preconditions, mints metadata with incremented generation, checksums, size, media link, storage class, and simulated clock update time, then inserts or replaces the sorted object entry. Appendable writer creation eventually calls `createOrUpdateFakeObject` with append mode, which reads existing object content and appends new bytes.

Listing computes a start name from prefix and continuation token, applies `StartOffset`, limits by prefix upper bound and max results, and emits either objects or collapsed runs depending on delimiter rules. It has extra HNS handling so folder entries representing prefixes are returned as prefixes rather than objects. Continuation tokens skip duplicate collapsed run results across pages.

Readers locate the object by name and optional generation, then slice content according to requested range and return a `FakeReader` with an opaque handle. Copy validates destination name, source existence/generation/metageneration, copies metadata/data, and assigns a fresh destination generation. Compose validates source count, reads each source, enforces component-count limits, creates the destination object, sets combined component count, and clears MD5 for composite behavior.

Stat panics for invalid extended-attribute requests that cannot be served from cache-like paths, returns not-found for missing objects, and optionally returns extended attributes. Update validates generation/metageneration then modifies object metadata and increments metageneration. Delete ignores missing objects and wrong generation, but enforces metageneration preconditions. Move validates source and destination, copies the record to the new name with new generation, removes the source, and re-sorts.

Folder operations maintain a separate sorted folder list plus prefix-object compatibility entries for HNS. `CreateFolder` creates both a folder record and a prefix object; `DeleteFolder` removes both if present; `RenameFolder` rewrites matching folder and object prefixes. `NewMultiRangeDownloader` validates object existence/generation and non-nil data before returning a fake downloader over that object.

## State and Persistence Behavior
All state is in memory under an invariant mutex: sorted object slice, sorted folder slice, and `prevGeneration`. Invariants ensure object names are strictly increasing and no object generation exceeds `prevGeneration`. Metadata maps are copied before returning to avoid exposing internal state. The fake uses the provided clock for object/folder creation and updates in most paths, though folder rename uses `time.Now()` directly.

## Dependencies and Integration Points
The fake bucket depends on `gcs` types and constants, `storageutil` conversions and object reads, `timeutil.Clock`, `syncutil.InvariantMutex`, checksum libraries, sorting, UTF-8 validation, path utilities, and standard IO. It is registered by `fake/bucket_test.go` against the common bucket test suite and is used by caching integration tests and other storage tests.

## Risks and Edge Cases
The fake intentionally approximates GCS and may diverge. It does not model multiple historical generations for one object, has mixed clock sources in `RenameFolder`, and `MoveObject` lacks explicit locking despite mutating shared slices. `CreateAppendableObjectWriter` calls `b.objects.find` without locking. HNS prefix/folder compatibility is subtle and easy to desynchronize. `DeleteObject` treats missing and wrong-generation deletes as success, which matches some idempotent test needs but may hide caller assumptions.

## Test Signals
The common fake bucket test registration in `bucket_test.go` exercises generic bucket behavior. Other files in this subset rely on this fake for cache integration and reader/downloader behavior. Specific risks around concurrent move/append locking and HNS folder semantics need targeted tests beyond the common suite.
