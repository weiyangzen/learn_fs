# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/OzoneSecurityUtil.java

## Purpose
`OzoneSecurityUtil` centralizes shared security helper logic for Ozone: security enablement, HTTP security enablement, authorization enablement including test mode, existence checks for key/cert files, and PEM string to `X509Certificate` conversion.

## Important APIs, types, and functions
- `isSecurityEnabled(ConfigurationSource conf)` initializes the security provider and reads `ozone.security.enabled`.
- `isHttpSecurityEnabled(ConfigurationSource conf)` requires full security plus HTTP Kerberos enablement.
- `isAuthorizationEnabled(ConfigurationSource conf)` enables authorization when full security or test authorization is enabled and `ozone.authorization.enabled` is true.
- `checkIfFileExist(Path path, String fileName)` checks directory and child-file existence.
- `convertToX509(List<String> pemEncodedCerts)` converts each PEM string through `CertificateCodec.readX509Certificate`.

## Control flow
The security predicates compose configuration booleans. `isAuthorizationEnabled` explicitly supports an authorization test mode that does not require full security. Certificate conversion iterates in input order and propagates `IOException`.

## State and persistence behavior
The utility is stateless, but `isSecurityEnabled` calls `SecurityConfig.initSecurityProvider`, which may initialize process-wide security provider state. File existence checks observe filesystem state and certificate conversion constructs in-memory certificate objects.

## Dependencies and integration points
It depends on HDDS `ConfigurationSource`, `SecurityConfig`, `CertificateCodec`, and Ozone config constants. It is used by Ozone services and tests to gate Kerberos, HTTP security, ACL/admin authorization, and certificate processing.

## Risks and edge cases
Calling `isHttpSecurityEnabled` and `isAuthorizationEnabled` also calls `isSecurityEnabled`, causing provider initialization side effects. `checkIfFileExist` only checks existence, not type, readability, permissions, or symlink safety. PEM conversion trusts `CertificateCodec` for validation and fails the entire conversion on the first bad certificate.

## Test signals
Tests should cover all combinations of security, HTTP security, authorization, and test-authorization flags; provider initialization idempotence; existing/missing file checks; unreadable/non-file paths if relevant; and valid/invalid PEM certificate conversion.
