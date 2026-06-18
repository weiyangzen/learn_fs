<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java

## Purpose
JAX-RS message body reader that accepts `text/plain` multipart-upload completion requests and returns an empty `CompleteMultipartUploadRequest`.

## Important APIs, types, and functions
- Annotated with `@Provider` and `@Consumes("text/plain")`.
- `isReadable` matches only `CompleteMultipartUploadRequest` with `MediaType.TEXT_PLAIN_TYPE`.
- `readFrom` ignores the body and returns a new empty completion request.

## Control flow
JAX-RS provider selection calls `isReadable`; if selected, `readFrom` prevents text/plain parsing failures by supplying an empty object.

## State and persistence behavior
No state is stored and no persistence occurs. It only influences request deserialization before endpoint logic.

## Dependencies and integration points
Integrated with `ObjectEndpoint.completeMultipartUpload`, which expects a `CompleteMultipartUploadRequest` parameter. It exists for AWS CLI behavior where `aws s3 cp` can send multipart requests as `text/plain`.

## Risks and edge cases
Returning an empty request can intentionally drive endpoint-level validation such as "must specify at least one part". A too-broad `isReadable` match would hide real malformed bodies for other resource methods.

## Test signals
Tests should send text/plain MPU completion/initiation style requests and verify the gateway returns S3 validation errors rather than a JAX-RS media parsing failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java -->
