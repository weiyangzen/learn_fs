<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java

## Purpose
JAX-RS exception mapper for generic `BadRequestException` values not represented as `OS3Exception`.

## Important APIs, types, and functions
- Annotated with `@Provider`.
- Implements `ExceptionMapper<BadRequestException>`.
- `toResponse` returns HTTP 400 with `exception.getMessage()` as the entity.

## Control flow
When JAX-RS raises `BadRequestException`, this mapper logs at debug level and builds a plain bad-request response.

## State and persistence behavior
Stateless; no persistence.

## Dependencies and integration points
Complements `OS3ExceptionMapper` for framework-level request parsing errors such as malformed parameters or body conversion failures.

## Risks and edge cases
The response body is not S3 XML error format, unlike `OS3Exception`. This can leak implementation-specific messages and can be less compatible with AWS clients.

## Test signals
Tests should verify malformed framework-level requests return 400 and decide whether S3 XML formatting is required for compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java -->
