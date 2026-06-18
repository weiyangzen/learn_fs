<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java

## Purpose
Shared conditional-header parsing and evaluation for S3 object reads, source-copy validation, and conditional writes.

## Important APIs, types, and functions
- `PreconditionContext` maps normal read headers and copy-source headers to common evaluation logic.
- `evaluatePreconditions` handles `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since`.
- `checkCopySourceModificationTime` supports the older copy-part modification-time flow.
- `parseWriteConditions` validates conditional PUT headers and returns `WriteConditions`.
- `WriteConditions` exposes `hasIfNoneMatch`, `hasIfMatch`, and parsed expected ETag.

## Control flow
Evaluation checks `If-Match` first, then `If-Unmodified-Since` only when no `If-Match` exists, then `If-None-Match`, then `If-Modified-Since`. READ context can return a 304 response with ETag and Last-Modified; COPY_SOURCE context throws 412 for failed conditions. Write parsing rejects empty values, simultaneous `If-Match` and `If-None-Match`, and any `If-None-Match` value other than `*`.

## State and persistence behavior
No persistent state is modified. The resulting `WriteConditions` drive Ozone create-if-absent or rewrite-if-match APIs in object write paths.

## Dependencies and integration points
Used by GET, HEAD, copy object, PUT, stream PUT, and MPU completion. Depends on Ozone key metadata, `OzoneUtils.formatDate`, `ObjectEndpoint` header helpers, `S3Utils.parseETag`, and `S3ErrorTable`.

## Risks and edge cases
Invalid date headers are ignored as non-matching AWS-style cache validation rather than hard failures. ETag matching supports comma-separated values and wildcard. The `If-Unmodified-Since` precedence differs when `If-Match` is present, so tests should pin compatibility. Write-side support is intentionally narrower than full HTTP semantics.

## Test signals
Tests should cover 304 responses, 412 failures, wildcard and comma ETag values, invalid date strings, copy-source header variants, unsupported conditional PUT combinations, missing keys with `If-Match`, and MPU completion precondition mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java -->
