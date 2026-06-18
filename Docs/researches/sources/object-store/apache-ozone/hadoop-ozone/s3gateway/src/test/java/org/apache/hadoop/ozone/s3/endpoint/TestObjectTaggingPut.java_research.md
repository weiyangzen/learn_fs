<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java

## Purpose
Tests `PUT Object tagging` XML parsing, validation, persistence, and unsupported FSO directory mapping.

## Important APIs, types, and functions
Uses `EndpointTestUtils.putTagging`, `S3Consts.S3_XML_NAMESPACE`, `OzoneKeyDetails.getTags`, `ObjectEndpoint`, S3 errors `MALFORMED_XML`, `NO_SUCH_KEY`, `NO_SUCH_BUCKET`, `NOT_IMPLEMENTED`, and `OMException.ResultCodes.NOT_SUPPORTED_OPERATION`.

## Control flow
Setup creates a bucket and empty object. Tests cover empty body, valid two-tag XML, malformed XML structure, missing `TagSet`, empty tags, missing key, missing value, missing object, missing bucket, and mocked FSO directory unsupported operation.

## State and persistence behavior
Valid tagging mutates only the key's tag map. Invalid XML and missing resources should not create or modify keys. Unsupported FSO directory behavior is translated without state change.

## Dependencies and integration points
This protects S3 tagging request XML unmarshalling and Ozone `putObjectTagging` integration.

## Risks and edge cases
Tag count, duplicate keys, and length constraints are mostly covered in PUT object tag-header tests rather than this XML endpoint.

## Test signals
Signals include exact persisted tag map for valid XML and expected S3 error categories for malformed, missing, and unsupported cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestObjectTaggingPut.java -->
