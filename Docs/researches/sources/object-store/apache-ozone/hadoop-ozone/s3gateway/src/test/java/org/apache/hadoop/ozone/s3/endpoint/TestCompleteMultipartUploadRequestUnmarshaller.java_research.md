<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java

## Purpose
Unit test coverage for `CompleteMultipartUploadRequestUnmarshaller`, the JAX-RS message-body reader that turns S3 CompleteMultipartUpload XML into a `CompleteMultipartUploadRequest`.

## Important APIs, types, and functions
The tests call `readFrom(...)` directly with `ByteArrayInputStream` bodies. They validate `CompleteMultipartUploadRequest.getPartList()`, nested `Part.getETag()`, and XML namespace handling with `S3Consts.S3_XML_NAMESPACE`.

## Control flow
Two basic tests feed XML with and without the S3 namespace, unmarshal it, and assert the parsed part order and ETag values. `concurrentParse` reuses one unmarshaller instance across 40 `CompletableFuture` tasks to catch unsafe shared parser state.

## State and persistence behavior
No persistent state is written. The relevant state is parser-local or unmarshaller-instance state that must not leak between concurrent reads.

## Dependencies and integration points
This protects multipart completion request parsing before `ObjectEndpoint.completeMultipartUpload` receives the part list. It depends on JAXB/JAX-RS unmarshalling behavior and the S3 XML namespace contract.

## Risks and edge cases
Coverage is focused on happy XML and thread reuse; malformed XML, missing fields, duplicate part numbers, and very large part lists are left to other layers.

## Test signals
Passing signals that namespaced and non-namespaced XML both produce two parts in order and that shared unmarshaller use is thread-safe for this request shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/endpoint/TestCompleteMultipartUploadRequestUnmarshaller.java -->
