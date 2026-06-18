<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java

## Purpose
JAX-RS mapper that turns `OS3Exception` into S3 XML HTTP responses.

## Important APIs, types, and functions
- Annotated with `@Provider`.
- Injects `RequestIdentifier`.
- `toResponse` sets the request ID on the exception, uses its HTTP code, and returns `exception.toXml()` as entity.

## Control flow
Endpoint code throws `OS3Exception`; JAX-RS invokes this mapper; the mapper adds request ID just before serialization.

## State and persistence behavior
Stateless aside from injected request identifier. No persistence.

## Dependencies and integration points
Integrated with all endpoint and auth errors that use `S3ErrorTable`. Depends on request ID infrastructure for AWS-style error tracing.

## Risks and edge cases
The mapper does not set an explicit XML content type. If `requestIdentifier` injection fails, request ID serialization may fail or be null depending on runtime behavior.

## Test signals
Tests should assert status code, XML body, request ID field, and behavior for customized `OS3Exception` messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java -->
