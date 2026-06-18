<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java

## Purpose
Tests `DELETE Object tagging` behavior.

## Important APIs, types, and functions
Uses `EndpointTestUtils.deleteTagging`, `put`, `ObjectEndpoint`, `OzoneClientStub`, `OzoneKeyDetails.getTags`, S3 errors `NO_SUCH_KEY`, `NO_SUCH_BUCKET`, and `NOT_IMPLEMENTED`.

## Control flow
Setup creates a tagged key. The success test deletes tags, expects HTTP 204, and verifies the key's tag map is empty. Error tests cover missing key and missing bucket. A mocked FSO-directory path throws `OMException.NOT_SUPPORTED_OPERATION`, which must map to S3 `NotImplemented`.

## State and persistence behavior
Only object tag metadata changes; object data remains. Unsupported directory tagging should not mutate mocked bucket state.

## Dependencies and integration points
This verifies `ObjectEndpoint.deleteTagging` integration with Ozone bucket `deleteObjectTagging`, OM exception translation, and S3 response status.

## Risks and edge cases
It does not verify idempotent delete on untagged existing objects or permission-denied paths, which are covered by permission tests.

## Test signals
Signals are HTTP 204, empty persisted tags, and expected S3 errors for not found and unsupported directory cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingDelete.java -->
