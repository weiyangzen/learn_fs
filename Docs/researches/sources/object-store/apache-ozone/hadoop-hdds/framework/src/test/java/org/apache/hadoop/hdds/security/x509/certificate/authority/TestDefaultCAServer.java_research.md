# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultCAServer.java

## Purpose

This test suite validates `DefaultCAServer` initialization, root and subordinate CA behavior, certificate requests, CSR subject validation, external root CA loading, certificate-chain loading, subordinate initialization, and certificate durations across daylight saving time.

## Important APIs, Types, And Functions

It uses `DefaultCAServer`, `CertificateServer`, `CertificateApprover.ApprovalType.TESTING_AUTOMATIC`, `DefaultProfile`, `DefaultCAProfile`, `SCMCertificateClient`, `CertificateCodec`, `CertificateSignRequest`, `SelfSignedCertificate`, `HDDSKeyGenerator`, `KeyStorage`, and security config keys for metadata and external root CA material.

## Control Flow

Each test builds temp-backed `OzoneConfiguration`, `SecurityConfig`, and `MockCAStore`. Root init creates or loads CA material and is checked for idempotence. Request tests generate CSRs, call `requestCertificate`, wait on completed futures, and inspect returned `CertPath`. External CA tests write key/cert material to configured locations before init. Subordinate CA tests first obtain/store a certificate from root CA, then initialize an SCM CA.

## State And Persistence

State includes temp metadata directories, generated key pairs, certificates written through `CertificateCodec` and `KeyStorage`, and no-op store behavior. External root and chain tests exercise file-backed certificate/key discovery.

## Dependencies And Integration Points

The suite integrates Bouncy Castle CSR/cert utilities, HDDS security config, SCM certificate client layout, CA profiles, Java certificate paths, and X.509 duration settings.

## Risks

The mock store omits real certificate persistence checks. Several tests rely on exact exception messages, wall-clock dates, timezone mutation, and random IDs. The daylight-saving test changes the JVM default timezone and must restore it to avoid cross-test leakage.

## Test Signals

Signals include non-null/idempotent CA certs, missing-cert/key initializer failures, cert path ordering with CA at index 1, issuer/subject linkage, invalid subject rejection, subordinate empty failure, external cert and chain selection, successful subordinate init, and exact max-duration milliseconds across DST.
