<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java

## Purpose
Tests XML serialization for `OS3Exception`.

## Important APIs, types, and functions
Uses `S3ErrorTable.newError(S3ErrorTable.ACCESS_DENIED, "bucket")`, `OS3Exception.setRequestId`, `OzoneUtils.getRequestID`, and `OS3Exception.toXml()`.

## Control flow
The test creates an AccessDenied exception, assigns a request ID, serializes it to XML, formats the expected XML string with code, message, resource, and request ID, and asserts exact equality.

## State and persistence behavior
No persistence. Exception state includes code, message, resource, and request ID; serialization must be deterministic.

## Dependencies and integration points
S3 error responses returned by Jersey exception mappers or endpoints depend on this XML shape for client compatibility.

## Risks and edge cases
The exact-string assertion is sensitive to formatting changes. Escaping special XML characters in fields is not covered.

## Test signals
Passing means `toXml()` emits the expected XML declaration and `Error` body fields for a representative S3 error.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/test/java/org/apache/hadoop/ozone/s3/exception/TestOS3Exceptions.java -->
