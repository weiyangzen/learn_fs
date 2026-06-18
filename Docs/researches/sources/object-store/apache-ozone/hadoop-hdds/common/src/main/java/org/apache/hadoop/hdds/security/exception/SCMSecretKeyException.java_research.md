# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecretKeyException.java

## Purpose
Exception for SCM secret key subsystem failures.

## Important APIs and types
The constructor accepts a message and `ErrorCode`. Codes include `OK`, `INTERNAL_ERROR`, `SECRET_KEY_NOT_ENABLED`, and `SECRET_KEY_NOT_INITIALIZED`.

## Control flow and state
It extends `IOException` and stores a final error code.

## Dependencies and integration points
Secret key managers and token/signature paths can use the error code to distinguish disabled, uninitialized, and internal states.

## Risks and test signals
Tests should verify code propagation and that callers distinguish disabled from uninitialized rather than treating all IO failures as transient.
