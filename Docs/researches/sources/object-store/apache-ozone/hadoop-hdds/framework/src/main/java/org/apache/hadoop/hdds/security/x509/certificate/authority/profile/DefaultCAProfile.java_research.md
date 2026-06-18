# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/DefaultCAProfile.java

## Purpose

`DefaultCAProfile` specializes `DefaultProfile` for CA certificate issuance. It permits CA basic constraints and adds certificate-signing usages.

## Important APIs, Types, and Functions

`isCA()` returns true. `getExtensionsMap()` inserts a validator for `Extension.basicConstraints`. `validateBasicExtensions` accepts only extensions whose parsed `BasicConstraints.isCA()` matches the profile CA status. `getKeyUsage()` includes digital signature, encipherment, key agreement, CRL signing, and certificate signing bits.

## Control Flow

The profile is consulted by `DefaultApprover` during CSR extension validation and when deciding which supported extensions to copy into a signed certificate.

## State and Persistence Behavior

No instance persistence is owned. It mutates `DefaultProfile.EXTENSIONS_MAP`, a static shared map, when `getExtensionsMap` is called.

## Dependencies and Integration Points

It depends on BouncyCastle `Extension`, `BasicConstraints`, `KeyUsage`, and the `PKIProfile` contract. It is used by `SCMCertificateClient` when initializing the primary SCM root CA.

## Risks and Edge Cases

The static extension map mutation is JVM-global and can make basic constraints appear supported for later non-CA default profiles. That is a subtle cross-profile coupling risk.

## Test Signals

Tests should validate CA basic constraints acceptance, non-CA constraints rejection, key usage bits, and isolation expectations when `DefaultCAProfile` and `DefaultProfile` are used in the same JVM.
