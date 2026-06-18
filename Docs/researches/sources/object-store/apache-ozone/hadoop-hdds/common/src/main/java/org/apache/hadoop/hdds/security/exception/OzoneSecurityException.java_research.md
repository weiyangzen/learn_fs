# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/OzoneSecurityException.java

## Purpose
Ozone-layer security exception carrying a domain result code.

## Important APIs and types
Constructors cover result-only, message/result, message/cause/result, and cause/result. `getResult()` returns `ResultCodes`, currently covering OM key-file absence, missing S3 secret, and secret-manager HMAC errors.

## Control flow and state
The exception is immutable after construction except for inherited throwable state.

## Dependencies and integration points
Callers can catch it as `IOException` while inspecting Ozone-specific result codes for protocol mapping or retries.

## Risks and test signals
Tests should assert result-code preservation in all constructors and mapping layers. Result-only construction has no detail message.
