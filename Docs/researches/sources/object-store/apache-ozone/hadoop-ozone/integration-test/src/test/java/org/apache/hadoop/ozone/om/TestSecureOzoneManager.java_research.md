# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestSecureOzoneManager.java

## Purpose
Unit-style integration coverage for secure OM certificate initialization. It exercises `OMCertificateClient` behavior for missing and partial key/certificate material and validates secure OM initialization failure reporting when the OM RPC address cannot be resolved for certificate signing.

## Important APIs and Types
The class `TestSecureOzoneManager` uses `OzoneConfiguration`, `OMStorage`, `SecurityConfig`, `OMCertificateClient`, `CertificateClient.InitResponse`, `KeyStorage`, `CertificateCodec`, `KeyStoreTestUtil`, `OzoneManager.initializeSecurity`, and `HddsProtos.OzoneManagerDetailsProto`. Important tests are `testSecureOmInitFailures` and `testSecureOmInitFailure`.

## Control Flow
`@BeforeEach` enables Ozone security, Kerberos authentication, ACLs, metadata dirs, and test secure OM mode, then builds OM details from the config. The main test constructs `OMCertificateClient` repeatedly while deleting or creating key/certificate files between cases. It checks init responses for first boot, existing keypair without certificate, missing public key, missing private key, certificate-only, private-key-plus-certificate, and full keypair-plus-certificate states. The second test sets an invalid OM address and asserts `initializeSecurity` throws a descriptive runtime exception.

## State and Persistence
The test persists private/public key files and certificate files in the temporary metadata/security directory. It also records certificate serial ID in `OMStorage`. The state matrix is intentionally mutated between client initializations to cover recovery/failure decisions.

## Dependencies and Integration Points
This connects OM security bootstrap, HDDS key storage layout, certificate codec, generated X.509 test certificates, SCM certificate acquisition path, Kerberos config, and OM address binding.

## Risks and Edge Cases
The test toggles `OzoneManager.setTestSecureOmFlag(true)` and does not reset it in this file, so suite-level isolation matters. Some cases pass null SCM IDs or clients intentionally, so response expectations encode bootstrap assumptions. File deletion order is critical for distinguishing missing-public-key from missing-private-key states.

## Test Signals
Signals include correct `GETCERT`, `FAILURE`, and `SUCCESS` responses for each local material combination, correct key/certificate object availability after init, and clear failure message when secure initialization cannot obtain an SCM-signed certificate for an unresolved OM address.
