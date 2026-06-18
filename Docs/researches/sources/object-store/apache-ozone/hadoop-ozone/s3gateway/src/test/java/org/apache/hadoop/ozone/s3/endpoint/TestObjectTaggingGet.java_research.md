<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java

## Purpose
Tests `GET Object tagging` response conversion from Ozone tag maps to S3 XML model objects.

## Important APIs, types, and functions
Uses `EndpointTestUtils.getTagging`, `put`, `S3Tagging`, `S3Tagging.Tag`, `TAG_HEADER`, and S3 errors `NO_SUCH_KEY` and `NO_SUCH_BUCKET`.

## Control flow
Setup creates a bucket and endpoint. A success test writes a key with two tags, retrieves tagging, and validates HTTP 200 plus tag keys and values. Another success test writes tags in reverse lexical order and asserts the response is sorted by key. Error tests cover missing key and bucket.

## State and persistence behavior
Tags are stored on `OzoneKeyDetails` in the stub bucket. GET tagging must read and sort them without mutating object metadata.

## Dependencies and integration points
This protects S3 XML marshalling model `S3Tagging` and Ozone object tag retrieval used by `ObjectEndpoint.getTagging`.

## Risks and edge cases
The tests do not cover empty tag sets on existing keys, XML serialization text, duplicate tag keys, or tag limits.

## Test signals
Signals are HTTP 200, non-null `S3Tagging.TagSet`, expected size and values, sorted key order, and not-found error mappings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingGet.java -->
