# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOmCertificateClientInit.java

## Purpose
`TestOmCertificateClientInit` validates `OMCertificateClient.init()` behavior for all combinations of private key, public key, and certificate presence on disk.

## Important APIs, Types, and Functions
- `OMCertificateClient.init()` returns `InitResponse` values `GETCERT`, `FAILURE`, or `SUCCESS`.
- `KeyStorage.storePrivateKey` and `storePublicKey` prepare key files.
- `CertificateCodec.writeCertificate` prepares the certificate file.
- `OzoneSecurityUtil.checkIfFileExist` asserts key files exist after non-failure initialization.

## Control Flow
Setup creates a temp metadata directory, `SecurityConfig`, generated key pair, self-signed certificate, mocked `OMStorage`, OM details proto, `OMCertificateClient`, and component key directory. The parameterized test deletes or writes private key, public key, and certificate files based on booleans, calls `init()`, asserts the expected response with a special case for both keys present but no cert, and verifies key files exist for non-failure responses.

## State and Persistence Behavior
This test writes actual key and certificate files under the temp security directory and deletes missing-case files with `FileUtils.deleteQuietly`. It verifies initialization can generate or preserve key material depending on present artifacts.

## Dependencies and Integration Points
The test integrates `SecurityConfig`, `HDDSKeyGenerator`, `KeyStorage`, `CertificateCodec`, `OMStorage`, `OzoneManager.getOmDetailsProto`, and Java `X509Certificate` generation via `KeyStoreTestUtil`.

## Risks and Edge Cases
Covered risks include partial key/cert states and ensuring successful init leaves both key files present. The test does not validate certificate chain trust, CSR submission, or SCM interaction because those are outside local init artifact handling.

## Test Signals
The file is a strong matrix test for local OM certificate-client bootstrap behavior and prevents regressions in key/cert artifact recovery.
