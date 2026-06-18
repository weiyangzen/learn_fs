<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java

## Purpose
Central table of S3-compatible error codes, messages, and HTTP status codes, plus translation from Ozone Manager exception result codes.

## Important APIs, types, and functions
- Enum values cover bucket/key not found, auth failures, invalid request/argument/range, MPU errors, ACL/tagging errors, quota/storage/digest errors, and conditional conflicts.
- `translateResultCode(OMException)` maps OM result codes to S3 errors.
- `newError` overloads construct `OS3Exception` by table entry, resource, cause, bucket/resource pair, or OM exception.
- `log` emits internal errors at error level and other errors at debug level.

## Control flow
Endpoint code catches `OMException` and calls `newError`, either with generic translation or special-case overrides. Translation maps access and token failures to `AccessDenied`, atomic write conflicts to `ConditionalRequestConflict`, ETag/key-exists failures to `PreconditionFailed`, and unknown results to `InternalError`.

## State and persistence behavior
Static immutable enum metadata only. No persistence.

## Dependencies and integration points
Used by every endpoint package and signature/parser utilities. It is the compatibility bridge between OM errors and S3 XML errors.

## Risks and edge cases
The translation table is a compatibility contract; adding OM result codes without updating it can expose `InternalError` for client errors. `NO_SUCH_BUCKET` uses bucket as resource in the bucket/resource overload, which differs from other errors.

## Test signals
Exception tests should pin every OM result translation used by endpoints, HTTP status codes, XML codes/messages, and special cases like conditional conflicts, digest mismatch, and bucket owner mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java -->
