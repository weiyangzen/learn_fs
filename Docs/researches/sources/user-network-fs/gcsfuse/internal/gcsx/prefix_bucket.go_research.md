# sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket.go

## Scope

This file implements `prefixBucket`, a `gcs.Bucket` decorator that presents a virtual bucket rooted at a configured object-name prefix. Calls entering the wrapper use local names without the prefix; calls leaving for the wrapped bucket prepend the prefix; returned object and folder names have the prefix stripped before they reach callers.

## Purpose

`NewPrefixBucket` lets higher layers mount or operate on a subtree-like view of a bucket without changing the underlying storage implementation. It preserves object-name UTF-8 invariants by rejecting invalid UTF-8 prefixes, and it delegates all persistence to the wrapped `gcs.Bucket`.

## Important APIs, Types, And Functions

- `NewPrefixBucket(prefix, wrapped)` validates `prefix` and returns a `gcs.Bucket`.
- `prefixBucket.wrappedName` and `localName` are the central name translators.
- Read paths: `NewReaderWithReadHandle` and `NewMultiRangeDownloader`.
- Write paths: `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, `FinalizeUpload`, and `FlushPendingWrites`.
- Mutation paths: `CopyObject`, `ComposeObjects`, `UpdateObject`, `DeleteObject`, `MoveObject`.
- Namespace paths: `ListObjects`, `GetFolder`, `CreateFolder`, `DeleteFolder`, `RenameFolder`.
- Metadata forwarding: `Name`, `BucketType`, and `GCSName`.

## Control Flow

Most methods clone the incoming request struct, rewrite only the name fields, call the wrapped bucket, and then strip the prefix from returned `Object`, `MinObject`, `Folder`, or listing names. `ListObjects` prepends the wrapper prefix to the request prefix and then trims it from both object names and collapsed runs. Compose rewrites every source name plus the destination name.

## State And Persistence Behavior

The wrapper stores only `prefix` and `wrapped`; all durable object, folder, upload, read-handle, and generation state lives in the wrapped bucket. Chunk and append writers are returned directly from the wrapped bucket, so finalization and flush are where returned min-object names are localized.

## Dependencies And Integration Points

The implementation depends on `internal/storage/gcs` bucket interfaces, `strings.TrimPrefix`, `unicode/utf8`, and `context`. It integrates with fake buckets and storage utilities in tests, with hierarchical namespace folder APIs, with multi-range downloading, and with GCS read handles.

## Risks And Maintenance Notes

Name translation must be kept complete as `gcs.Bucket` grows. Any new method that accepts or returns object/folder names needs explicit prefix mapping. `localName` uses `strings.TrimPrefix`, so it silently returns unchanged names if a wrapped implementation returns an object outside the prefix; this is useful for defensive behavior but may hide wrapped-bucket bugs. `RenameFolder` prefixes `destinationFolderId` as though it is a folder name; this is correct only if that field semantically expects a prefixed name/id in the wrapped API. `GCSName` composes with `wrapped.GCSName(object)`, so wrappers beneath this one can affect final naming.

## Test Signals

Coverage comes from `prefix_bucket_test.go`: normal reads, read handles, MRD reads and errors, object create/copy/compose/stat/list/update/delete, chunk writer finalize/flush, appendable writer flows, folders, and hierarchical object move. The tests assert both local returned names and back-door wrapped-bucket storage names.
