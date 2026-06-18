# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/profile/PKIProfile.java

## Purpose

`PKIProfile` defines the executable PKI policy contract used by Ozone certificate approval. It abstracts allowed subject names, extensions, key purposes, key usage, RDNs, and CA capability.

## Important APIs, Types, and Functions

The interface exposes `getGeneralNames`, `isSupportedGeneralName`, `validateGeneralName`, `getSupportedExtensions`, `isSupportedExtension`, `validateExtension`, `validateExtendedKeyUsage`, `getKeyUsage`, `getRDNs`, `isValidRDN`, `validateRDN`, `isCA`, and `getExtensionsMap`.

## Control Flow

`DefaultApprover.inspectCSR` and `sign` use this contract to validate CSR contents and decide which requested extensions can be copied into issued certificates.

## State and Persistence Behavior

No state or persistence is prescribed. Implementations can be immutable or dynamic; the default implementation uses in-memory sets/maps.

## Dependencies and Integration Points

It integrates BouncyCastle `GeneralName`, `Extension`, `KeyPurposeId`, `KeyUsage`, and `RDN` policy primitives with Ozone CA code.

## Risks and Edge Cases

Implementations control security policy; overly permissive RDN/general-name/extension validation directly affects issued certificate scope. `getExtensionsMap` exposes the validator map and can allow mutation depending on implementation.

## Test Signals

Profile implementation contract tests should verify all supported/unsupported extension paths, CA versus non-CA behavior, and invalid subject-name rejection under the concrete implementation.
