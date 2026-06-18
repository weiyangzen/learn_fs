# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/S3BlobStore.h

## Purpose
`S3BlobStore.h` declares the S3-compatible implementation of `IBlobStoreEndpoint`. It covers endpoint parsing, credential loading, request signing, retry hooks for token errors, object and bucket operations, listing, multipart upload, object tags, and URL construction.

## Important APIs, Types, And Functions
- `S3BlobStoreEndpoint` inherits `IBlobStoreEndpoint` and `ReferenceCounted`.
- `Credentials` stores key, secret, and security token.
- The constructor accepts host, service, region, proxy settings, optional credentials, blob knobs, and extra HTTP headers.
- `guessRegionFromDomain()` infers cloud region from known S3/COS style hostnames.
- `fromString()` downcasts the generic `IBlobStoreEndpoint::fromString()` result to S3.
- Credential APIs include `updateSecret()`, `extractCredentialFields()`, `credentialFileKey()`, and `lookupSecretOnEachRequest()`.
- Request APIs include `setRequestHeaders()`, `normalizeResourceForRequest()`, `setAuthHeaders()`, `setV4AuthHeaders()`, failure simulation/processing, and `preRetryCheck()`.
- Object APIs include list buckets/objects, existence/size/read/delete/create bucket, read/write entire files, multipart begin/upload/finish/abort, and tag put/get.

## Control Flow And State
Requests normalize resources, apply headers, sign with either legacy HMAC-SHA1 or AWS V4 style headers, then use inherited blob store request machinery. Token or credential failures can set `retryExtended` and run `preRetryCheck()` before retry. Multipart uploads begin with an upload ID, upload numbered parts with content hashes, then finish with a part set and optional total size.

## Persistence And External State
State includes optional credentials, lookup flags, simulated token error flag, endpoint/proxy/knob state inherited from `IBlobStoreEndpoint`, and extra headers. External persistence is remote S3-compatible bucket/object data and credential files or secret providers.

## Dependencies And Integration Points
It depends on Flow packet queues, `IBlobStore`, and HTTP RPC types. It is used by backup/restore, blob storage, bulk dump/load, and command-line S3 client helpers. The URL format is shared with `S3Client.h`.

## Risks And Edge Cases
Signature construction is security-critical and sensitive to resource normalization, date formats, headers, region, and temporary security tokens. Credential refresh on retry must avoid infinite retry loops and stale secrets. `fromString()` can return null if a non-S3 endpoint parses. Listing with recursive delimiters can fan out many requests. Multipart completion must preserve part order and eTags.

## Test Signals
Tests should cover URL parsing, region guessing, credential extraction/refresh, V2/V4 auth header golden cases, proxy handling, resource normalization, simulated token failures, retry extension, bucket/object existence, ranged reads, multipart upload lifecycle, tag operations, recursive listing, and S3-compatible provider variants.
