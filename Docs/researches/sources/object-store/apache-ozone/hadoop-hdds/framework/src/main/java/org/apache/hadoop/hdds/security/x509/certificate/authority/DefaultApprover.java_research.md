# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultApprover.java

## Purpose

`DefaultApprover` implements the default CSR inspection and certificate signing policy for Ozone's in-process CA. It verifies CSR proof-of-possession, checks requested RDNs and extensions against a `PKIProfile`, enforces SCM/cluster identity, validates key size, and emits an X.509 certificate signed by the CA private key.

## Important APIs, Types, and Functions

Constructor arguments are `PKIProfile` and `SecurityConfig`. `sign(...)` builds signature and digest algorithm identifiers, extracts subject OU/O/CN, handles the datanode pre-registration `null` SCM/cluster special case, rebuilds the subject with serial number, validates RSA modulus length against `config.getSize()`, copies supported CSR extensions, and returns a `JcaX509CertificateConverter` result. `inspectCSR` returns a future after `verifyPkcs10Request`, `profile.validateRDN`, and `verfiyExtensions`. Helper methods decode PKCS#9 extension attributes.

## Control Flow

Inspection is staged: validate CSR signature, validate each RDN, validate each requested extension. Signing then performs identity and key checks before constructing `X509v3CertificateBuilder` and signing with `BcRSAContentSignerBuilder`.

## State and Persistence Behavior

The approver owns no persistence; it is a pure policy/signing component over supplied key and certificate material.

## Dependencies and Integration Points

It depends heavily on BouncyCastle ASN.1, PKCS#10, X.509 builder, content signer/verifier APIs, `PKIProfile`, `CertificateSignRequest` helpers, and `SCMSecurityException`. It is created by `DefaultCAServer.init`.

## Risks and Edge Cases

The method assumes OU, O, and CN RDNs are present at index zero; malformed subjects can throw runtime exceptions. `inspectCSR` can call `completeExceptionally` and still continue checking later stages because it does not return immediately after failure. The misspelled `verfiyExtensions` is visible to tests. Only RSA public keys are accepted by the cast to `RSAKeyParameters`.

## Test Signals

Coverage should include valid CSR signing, invalid CSR signature, unsupported extension, unsupported RDN, key size too small, cluster/SCM mismatch, datanode null SCM/cluster substitution, missing RDNs, CA extension handling, and returned certificate subject/issuer/serial/validity.
