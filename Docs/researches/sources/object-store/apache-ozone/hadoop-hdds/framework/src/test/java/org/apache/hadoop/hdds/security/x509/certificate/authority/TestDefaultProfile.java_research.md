# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/authority/TestDefaultProfile.java

## Purpose

This class tests the default PKI profile and approver validation for supported subject alternative names, CSR signature verification, CA constraints, SAN criticality, unsupported SAN types, and extended key usage.

## Important APIs, Types, And Functions

It uses `DefaultProfile`, `DefaultApprover`, `CertificateSignRequest.Builder`, `HDDSKeyGenerator`, Bouncy Castle `PKCS10CertificationRequest`, `ExtensionsGenerator`, `GeneralName`, `Extension.subjectAlternativeName`, `ExtendedKeyUsage`, and `KeyPurposeId`.

## Control Flow

Setup creates temp-backed security config, a profile, approver, and key pair. Tests generate valid CSRs through Ozone's builder or manually build CSRs with selected extensions. Assertions call `isSupportedGeneralName`, `verifyPkcs10Request`, and `verfiyExtensions`.

## State And Persistence

State is in-memory key pairs, CSRs, extensions, and security config. No certificates are persisted.

## Dependencies And Integration Points

The suite integrates certificate request construction with CA profile validation rules used by `DefaultCAServer`.

## Risks

The helper `getInvalidCSR` ignores its `kPair` parameter and uses the field `keyPair`, which is harmless here but misleading. The method name `verfiyExtensions` reflects production spelling. Criticality and supported-name assertions are policy guards that require intentional updates when profile rules change.

## Test Signals

Signals include support for IP, DNS, and otherName; rejection of directory and email names; valid CSR signature; invalid key-pair signature failure; valid normal extensions; CA extension rejection; email/URI SAN rejection; critical DNS rejection with noncritical DNS acceptance; client/server EKU acceptance; critical clientAuth and OCSP EKU rejection.
