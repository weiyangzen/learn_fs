# sources/user-network-fs/rclone/backend/s3/s3_internal_test.go

## Purpose
This file contains S3 backend internal and integration-style tests that require a live backend instance. It validates metadata preservation, gzip handling, no-HEAD upload behavior, version listing semantics, delete marker merging, `aws-chunked` content-encoding cleanup, bucket-creation quirks, hidden-version cleanup, and S3 Object Lock support.

## Important APIs, Types, And Functions
Helper functions `gz` and `md5sum` build compressed test payloads and expected hashes. Methods on `*Fs` implement the `fstests.InternalTester` contract: `InternalTestMetadata`, `InternalTestNoHead`, `InternalTestVersions`, `InternalTestObjectLock`, and umbrella `InternalTest`. Standalone tests cover `versionLess`, `mergeDeleteMarkers`, and `removeAWSChunked`.

`InternalTestMetadata` writes an object with system metadata and user metadata, then reads it back through `Object.Metadata` and exercises downloads with and without `f.opt.Decompress`. `InternalTestVersions` enables bucket versioning, writes/removes/rewrites a file, then checks `--s3-versions`, `--s3-version-at`, version-suffixed object lookup, `NewFs` file-root detection, bucket already-exists quirk inference, and `CleanUpHidden`. `InternalTestObjectLock` creates a temporary Object Lock-enabled bucket and tests retention, legal hold, after-upload Object Lock APIs, multipart Object Lock upload, and presigned Object Lock upload.

## Control Flow
The tests mutate `f.opt` directly around subtests and restore settings with defers. Live S3 state is prepared by uploading objects with `fstests.PutTestContents` or direct SDK calls, then validated through normal backend methods. Version tests intentionally sleep between operations because AWS S3 LastModified precision may be one second. Object Lock tests create and later tear down a dedicated bucket, including explicit version/delete-marker cleanup with `DeleteObjects`.

## State And Persistence Behavior
These tests create real objects, object versions, delete markers, bucket versioning state, and an Object Lock-enabled temporary bucket. They use defers to remove objects, suspend versioning, reset backend options, clear legal holds, bypass governance retention for cleanup, and delete the temporary bucket. The tests also verify cached object metadata by clearing `o.meta` in the legal-hold subtest before re-reading.

## Dependencies And Integration Points
The file depends on rclone `fstest` and `fstests`, AWS SDK S3 types, Smithy API errors, bucket path helpers, random string generation, version path helpers, and testify assertions. It is tightly coupled to unexported backend internals such as `f.opt`, `setGetVersioning`, `pacer`, `rootBucket`, `setObjectLegalHold`, and the delete-marker sentinel.

## Risks And Edge Cases
Tests are provider-sensitive. Impossible Cloud and Cloudflare get special handling for metadata/gzip behavior. Object Lock tests skip when quirks say unsupported or when the provider accepts bucket flags without functional Object Lock. Direct mutation of `f.rootBucket` and options makes cleanup correctness important, especially under failures. Time-based version tests can be slow and rely on provider timestamp precision. The `removeAWSChunked` expectations intentionally remove spaces around remaining tokens when `aws-chunked` was present, so formatting changes in that helper may require test updates.

## Test Signals
This file is itself a major test signal for the backend. It complements generic `fstests` by checking behavior not fully covered by the public `fs.Fs` contract: provider metadata fidelity, version and delete-marker semantics, Object Lock API compatibility, and low-level helper behavior.
