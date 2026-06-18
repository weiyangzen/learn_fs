# sources/storage-engines/foundationdb/fdbclient/GCSBlobStore.cpp

## Purpose
`GCSBlobStore.cpp` implements Google Cloud Storage support on top of the existing S3-compatible XML blob-store implementation. It specializes request authentication, credential-file parsing, URL round-tripping, and bucket creation while inheriting object list/read/write/multipart behavior from `S3BlobStoreEndpoint`.

## Important APIs, Types, And Functions
The central type is `GCSBlobStoreEndpoint`. Its constructor delegates to `S3BlobStoreEndpoint` without S3 credentials, stores `projectId`, extracts an optional bearer token from URL credentials, and records whether tokens must be looked up from credential files. Overridden methods are `setRequestHeaders()`, `updateSecret()`, `extractCredentialFields()`, `lookupSecretOnEachRequest()`, `credentialFileKey()`, `getResourceURL()`, and `createBucket()`. The actor helper `createBucket_gcs_impl()` performs rate limiting, existence check, project-id validation, and the GCS bucket `PUT`.

## Control Flow
For each request, `setRequestHeaders()` sets `Accept: application/xml`, adds `Authorization: Bearer <token>` if present, and adds `x-goog-project-id` when configured. `updateSecret()` bypasses S3's credential short-circuit and invokes `IBlobStoreEndpoint::updateSecret()` so token refresh works even though S3 access-key credentials are intentionally absent. `extractCredentialFields()` accepts JSON objects with a `token` field. `getResourceURL()` appends provider parameters (`p=gcs` and optional `gcspid`) and re-inserts inline tokens only when they came from the original URL. `createBucket()` waits for write allowance, returns if the bucket already exists, requires `projectId`, and issues an S3-style XML API `PUT`.

## State And Persistence Behavior
Endpoint state consists of `projectId`, `token`, and `lookupToken`. Tokens supplied inline are serialized back into generated blobstore URLs; refreshed credential-file tokens are deliberately omitted to avoid persisting short-lived secrets into URLs. The only remote persistent mutation in this file is bucket creation through the GCS XML API.

## Dependencies And Integration Points
The implementation depends on `GCSBlobStore.h`, `fdbclient/JSONDoc.h`, `flow/Trace.h`, `S3BlobStoreEndpoint`, `IBlobStoreEndpoint`, `BlobKnobs`, HTTP headers, endpoint request-rate limiters, and FoundationDB actor futures. Integration with URL parsing is via `S3BlobStoreEndpoint::fromString()` selecting this subclass when `p=gcs` or `provider=gcs` is present.

## Risks And Edge Cases
Missing `projectId` makes bucket creation fail with `backup_invalid_url()`, although non-create operations can run without it. Inline tokens are secrets in serialized URLs; refreshed tokens are intentionally not serialized, so callers must understand the difference. `extractCredentialFields()` rejects credential JSON without `token`, and no expiry metadata is represented here. The bucket-create request accepts `200` and `409`; other GCS XML API variants or permission errors surface through the inherited request path.

## Test Signals
This file includes unit tests for URL parsing, long and short provider parameters, non-GCS URL behavior, request headers with and without token/project ID, URL generation with `p=gcs`/`gcspid`, inline-token round-trip, and omission of credential-file tokens from serialized URLs.
