<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java

## Purpose
Runtime exception type representing an S3-compatible error response, including error code, message, resource, request ID, HTTP status, and XML serialization.

## Important APIs, types, and functions
- JAXB annotations map fields to S3 `<Error>` XML.
- Package-private constructor accepts `S3ErrorTable`, cause, and resource.
- `toXml` serializes through Jackson `XmlMapper` with JAXB annotations and XML declaration.
- `withMessage` customizes the S3 error message fluently.

## Control flow
`S3ErrorTable.newError` constructs the exception and logs it. `OS3ExceptionMapper` later sets request ID and serializes it as the HTTP entity.

## State and persistence behavior
Only in-memory exception state is held. No persistence occurs.

## Dependencies and integration points
Used throughout endpoint, auth, util, and exception mapping code. Depends on Jackson XML, JAXB annotations, and `S3ErrorTable`.

## Risks and edge cases
Serialization fallback manually formats XML if Jackson fails. `super` message remains the original table message even if `withMessage` or `setErrorMessage` changes the XML message. Request ID is injected later, so logging at construction may show null request ID.

## Test signals
`TestOS3Exceptions` checks XML and code/message behavior. Additional tests should cover customized messages, resource fields, request ID injection, and mapper HTTP status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java -->
