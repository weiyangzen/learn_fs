# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/CertificateTestUtils.java

## Purpose
Provides reusable helpers for tests that need RSA key pairs and self-signed X.509 certificates.

## Important APIs, types, and functions
- Public helpers include `aKeyPair`, overloaded `createSelfSignedCert`, `subjectKeyIdOf`, `authorityKeyIdOf`, `pubKeyInfo`, and `extensionUtil`.
- Uses `SecurityConfig`, `HDDSKeyGenerator`, Bouncy Castle `X500Name`, `X509v3CertificateBuilder`, `JcaX509CertificateConverter`, key identifier utilities, and SHA/RSA algorithm identifiers.

## Control flow
Helpers generate a key pair from security configuration, build subject/issuer names and validity windows, attach basic constraints and key identifier extensions, sign the certificate, and convert it to a Java `X509Certificate`.

## State and persistence behavior
All certificate and key material is generated in memory. No files are written by this utility.

## Dependencies and integration points
This file is shared test infrastructure for HDDS certificate-authority, key, and TLS tests. It integrates Ozone security config with Bouncy Castle certificate generation.

## Risks and test signals
The helper can mask production certificate requirements if extensions or algorithms drift. Tests using it depend on sane validity periods, key IDs, and provider setup.
