<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java

## Purpose
Tests `HEAD Object` metadata response behavior and conditional handling.

## Important APIs, types, and functions
Uses `ObjectEndpoint.head`, `EndpointTestUtils.put`, `assertStatus`, `assertErrorResponse`, condition headers (`IF_MATCH_HEADER`, `IF_NONE_MATCH_HEADER`, `IF_UNMODIFIED_SINCE_HEADER`), `TAG_HEADER`, `TAG_COUNT_HEADER`, `RFC1123Util`, and FSO directory creation config.

## Control flow
Setup creates a stub bucket and endpoint. Tests create keys, call `head`, and assert status, content length, `Last-Modified`, and tag-count behavior. Conditional tests verify matching ETag success, `If-None-Match` not-modified, failed `If-Unmodified-Since`, and precedence when `If-Match` succeeds. FSO tests distinguish file paths, directory paths with slash, directory paths without slash, and file path with trailing slash.

## State and persistence behavior
Stub key metadata includes content length, modification time, ETag, and tags. `HEAD` reads this state without returning a body and applies path interpretation for FSO directories.

## Dependencies and integration points
This protects metadata presentation shared with GET, S3 conditional request logic, and directory-key compatibility.

## Risks and edge cases
Date parsing is tested through generated values only; invalid condition dates and custom response overrides are not covered here.

## Test signals
Signals are HTTP 200/304/404, `PRECOND_FAILED`, content-length equality, parseable last-modified, and `x-amz-tagging-count` inclusion only for tagged objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectHead.java -->
