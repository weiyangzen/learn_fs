<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java

## Purpose
Handles S3 object tagging subresource requests, namely `PUT ?tagging`, `GET ?tagging`, and `DELETE ?tagging`.

## Important APIs, types, and functions
- Uses a memoized `MessageUnmarshaller<S3Tagging>` for XML request bodies.
- `handlePutRequest` parses XML, validates required tag fields, then calls `OzoneBucket.putObjectTagging`.
- `handleGetRequest` calls `getObjectTagging` and serializes `S3Tagging.fromMap`.
- `handleDeleteRequest` calls `deleteObjectTagging` and maps missing keys to `NoSuchKey`.
- `getAction` detects supported methods when query parameter `tagging` is present.

## Control flow
The handler first calls `context.ignore(getAction())`; if no tagging action applies it returns `null`. For PUT, XML parsing and semantic validation happen before converting to Ozone tag maps via endpoint tag validators. Success and failure update operation-specific tagging metrics.

## State and persistence behavior
PUT persists the tag map on the object through Ozone bucket metadata. DELETE removes the object's tag set. GET is read-only and returns sorted tag XML through `S3Tagging.fromMap`.

## Dependencies and integration points
Depends on object endpoint context for bucket lookup, `S3Tagging`, `MessageUnmarshaller`, endpoint tag validation helpers, `S3GatewayMetrics`, `S3Consts.QueryParams.TAGGING`, and OM exception result codes.

## Risks and edge cases
Malformed XML is converted to `MalformedXML` with the parser message appended. Delete tagging is intentionally stricter than object deletion: missing keys are errors, not 204. Tag value validation is split between XML structural checks and endpoint-level tag policy validation.

## Test signals
Tests should cover empty/missing `TagSet`, missing key/value fields, duplicate or invalid tags, sorted GET responses, missing-key delete behavior, and metric success/failure counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java -->
