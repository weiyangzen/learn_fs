# sources/storage-engines/foundationdb/fdbclient/S3BlobStore.cpp

## Purpose
`S3BlobStore.cpp` implements the S3-compatible `IBlobStoreEndpoint` backend used by backup/restore and blob operations. It handles bucket/object APIs, S3 URL/resource construction, credentials, AWS v2/v4 signing, request retry support for expiring tokens, listing, multipart upload, object integrity checks, tags, and unit tests.

## Important APIs, Types, and Functions
- `guessRegionFromDomain` infers regions from common S3-compatible host patterns and special-cases localhost.
- `parseS3Credentials`, `updateSecret`, `extractCredentialFields`, `credentialFileKey`, and `lookupSecretOnEachRequest` manage inline, file-backed, and optional AWS SDK credentials.
- `constructResourcePath` supports virtual-hosted and path-style bucket addressing and strips leading slashes from object keys.
- Bucket/object operations include `bucketExists`, `objectExists`, `deleteObject`, `createBucket`, `objectSize`, `readEntireFile`, `writeEntireFileFromBuffer`, and `readObject`.
- Listing APIs include `listObjectsStream` using ListObjectsV2 pagination and recursive common-prefix handling, plus `listBuckets`.
- Signing helpers include `awsCanonicalURI`, `hmac_sha1`, SHA256 helpers, `setV4AuthHeaders`, and `setAuthHeaders`.
- Multipart APIs include begin, upload part, finish, and abort.
- Tag APIs include `putObjectTags` with verify/retry and `getObjectTags`.
- `parseErrorCodeFromS3`, `isS3TokenError`, `processRequestFailure`, and `preRetryCheck` support token-error retry handling.

## Control Flow and State
Each public method wraps a reference-counted actor implementation. Operations acquire rate-limiter allowance, build a resource path, set headers, and call `doRequest` inherited from the blob-store base. Write operations also use upload concurrency locks. Listing loops over truncated responses with continuation tokens and sends parsed `ListResult` pages to a promise stream; recursive listing queues sub-list futures.

Signing builds canonical resource/query/header data. V4 signing adds `x-amz-content-sha256`, `x-amz-date`, signed headers, credential scope, and HMAC-SHA256 authorization. Legacy signing builds the AWS string-to-sign with date, content headers, x-amz/x-icloud headers, and canonical resource.

Token retry support parses S3 XML error codes, treats `InvalidToken` and `ExpiredToken` 400 responses specially, and for write retries can perform a dry-run bucket request before resending a large write.

## State and Persistence Behavior
Persistent state lives in S3 buckets and objects, object tags, multipart upload sessions, and remote bucket metadata. Local state includes endpoint credentials, region, request knobs, rate limiters/locks inherited from the base class, and `simulatedTokenError` for simulation fault injection. Object integrity can persist checksum metadata through S3 headers.

## Dependencies and Integration Points
The file depends on `S3BlobStore.h`, `fdbrpc/HTTP`, blob/client knobs, Flow networking/tracing/actors, OpenSSL SHA/HMAC, MD5, SHA1, base64, Boost string algorithms, RapidXML, async file interfaces, host parsing, and optional `FDBAWSCredentialsProvider` under `WITH_AWS_BACKUP`. It integrates directly with backup and restore blob-store URL handling.

## Risks and Edge Cases
- V4 signing requires a non-empty region; region inference may fail for uncommon S3-compatible domains unless explicitly configured.
- URL/resource canonicalization is security- and compatibility-sensitive, especially query sorting, path encoding, virtual hosting, and object keys with leading slashes.
- XML parsing with RapidXML mutates buffers and can throw on malformed or non-XML responses; most paths convert these to HTTP errors, but diagnostics depend on response shape.
- Multipart completion after a client-side timeout is acknowledged as ambiguous; retry may see a removed upload ID.
- `putObjectTags` builds XML by string concatenation without escaping tag keys/values.
- Token dry-run retry applies only to write requests when enabled and depends on parsing a bucket from path-style resources.
- The SHA256 integrity path relies on S3 returning `x-amz-checksum-sha256` on GET after uploads.

## Test Signals
The file includes unit tests for AWS V4 authorization headers, region guessing and invalid URL overflow, virtual-hosted list path construction, resource path normalization, and S3 error-code parsing for XML, HTML, empty, and malformed responses. Additional high-value tests should cover multipart checksum manifests, tag XML escaping, recursive listing with continuation tokens, token retry dry-run paths, virtual-hosted write retries, and integrity-check read failures.
