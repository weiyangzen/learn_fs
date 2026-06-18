# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/exception/CertificateException.java

## Purpose
SCM security exception subtype for X.509 certificate client/server failures.

## Important APIs and types
Constructors accept message, cause, message/cause, message/error code, and message/cause/error code. `errorCode()` returns a certificate-specific `ErrorCode` such as keystore, crypto signing, CSR, bootstrap, renew, rollback, or signature verification errors.

## Control flow and state
It extends `SCMSecurityException` but stores its own mutable-looking package-private `errorCode` field rather than using the superclass error-code taxonomy.

## Dependencies and integration points
Certificate client, CA, CSR, and rotation code can throw this type for X.509-specific failure handling.

## Risks and test signals
Tests should verify certificate-specific code propagation. Callers must use `errorCode()` rather than `getErrorCode()` from `SCMSecurityException` if they need the certificate-specific enum.
