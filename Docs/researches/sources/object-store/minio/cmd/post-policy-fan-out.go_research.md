# sources/object-store/minio/cmd/post-policy-fan-out.go

## Purpose
This file implements POST object fan-out, allowing one incoming buffer to be written to multiple object keys with per-entry metadata and tags.

## Important APIs, Types, and Functions
`fanOutOptions` carries encryption type, key material, KMS context, checksum, and MD5 hex. `fanOutPutObject` accepts fan-out entries and the buffered object content, then returns per-entry `ObjectInfo` and error slices.

## Control Flow and State
The function launches one goroutine per fan-out entry. Each goroutine builds a hash reader over the shared immutable byte slice, copies metadata, parses tags, optionally wraps encryption with `newEncryptReader`, and calls `objectAPI.PutObject` with versioning flags from `globalBucketVersioningSys`. Errors are stored by entry index.

## Dependencies and Integration Points
It depends on MinIO's hash reader, encryption/KMS helpers, object-layer `PutObject`, versioning system, and minio-go fan-out entry definitions.

## Risks and Test Signals
Fan-out concurrency can amplify memory and object-layer load because every entry reads from the same in-memory buffer. Error assignment in deferred closes can overwrite earlier errors for an entry. Encryption disables content verification through a new hash reader with unknown size. No direct tests in this subset.
