# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/exception/SCMSecurityException.java

## Purpose
Root `IOException` subtype for SCM security and certificate-related failures.

## Important APIs and types
Constructors support message, message/error code, message/cause, message/cause/error code, cause/error code, and cause-only. `ErrorCode` covers CSR errors, certificate issuance/fetch failures, PEM encoding, missing or failed block tokens, root CA fetch failures, and non-primary SCM errors.

## Control flow and state
The final error code defaults to `DEFAULT` unless explicitly supplied.

## Dependencies and integration points
Certificate utilities, token verification, SCM security APIs, and protocol mappers use this as the common checked exception.

## Risks and test signals
Tests should assert code preservation and defaulting behavior. Mapping code should not lose specific codes such as `BLOCK_TOKEN_VERIFICATION_FAILED`.
