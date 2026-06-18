<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java

## Purpose
Validates `GET Object` response behavior for content metadata, conditionals, range requests, tags, and FSO directory handling.

## Important APIs, types, and functions
Uses `EndpointTestUtils.get/put`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneClientTestUtils.assertKeyContent`, conditional headers (`If-Match`, `If-None-Match`, `If-Modified-Since`, `If-Unmodified-Since`), `RANGE_HEADER`, response override query params, and `TAG_COUNT_HEADER`.

## Control flow
Setup creates a bucket, a normal key, and a tagged key. Tests assert basic headers, valid and failing ETag preconditions, not-modified status for time/ETag conditions, precedence of ETag conditions over date conditions, tag-count header inclusion only for tagged objects, response header inheritance/override, range content length/content range/status 206, and FSO directory lookup behavior when directory creation is enabled.

## State and persistence behavior
Object data, metadata, modification time, and tags are stored in the stub bucket. GET must not mutate object state, but it must expose stored metadata through HTTP headers and stream selected byte ranges.

## Dependencies and integration points
This covers S3 conditional request evaluation, RFC1123 date formatting, range parsing, response header override query handling, and FSO directory semantics.

## Risks and edge cases
Streaming response bodies are not fully consumed in every test. Multi-range requests, invalid ranges, and timezone edge cases are only indirectly covered.

## Test signals
Signals include exact HTTP status codes, content-length/range headers, parseable `Last-Modified`, tag count values, and expected `PreconditionFailed`/`NoSuchKey` errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectGet.java -->
