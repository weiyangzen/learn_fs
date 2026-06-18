<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java

## Purpose
Tests custom XML unmarshalling for S3 multi-object delete requests.

## Important APIs, types, and functions
Exercises `MultiDeleteRequestUnmarshaller.readFrom`, `MultiDeleteRequest.getObjects()`, and XML namespace handling via `S3Consts.S3_XML_NAMESPACE`.

## Control flow
Two tests build compact delete XML with three object entries, once with the S3 namespace and once without it, then invoke `readFrom` and assert the resulting request contains three objects.

## State and persistence behavior
No persistent state is involved. The parser must create an independent request object from the request body so `BucketEndpoint.multiDelete` can later apply deletes.

## Dependencies and integration points
This parser is the request-body adapter for the bucket multi-delete endpoint. Correct parsing affects deletion response content and quiet-mode behavior downstream.

## Risks and edge cases
The test body uses `<Object>key</Object>` rather than validating all S3 nested `<Object><Key>...` variants. It does not cover malformed XML, quiet flags, whitespace, duplicate objects, or invalid encodings.

## Test signals
Passing means namespaced and non-namespaced delete bodies both produce the expected object count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestMultiDeleteRequestUnmarshaller.java -->
