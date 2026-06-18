# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/utils/CertificateSignRequest.java

## Purpose

`CertificateSignRequest` builds, encodes, and decodes PKCS#10 CSRs for Ozone components. Its builder assembles subject identity, key usage, basic constraints, and subject alternative names before signing the CSR with the component private key.

## Important APIs, Types, and Functions

Static DN helpers expose `CN=%s,OU=%s,O=%s` and serial-number variants. `getPkcs9ExtRequest` and `getPkcs9Extensions` extract CSR extension requests. `toEncodedFormat` writes PEM `CERTIFICATE REQUEST`. `generateCSR` builds a `JcaPKCS10CertificationRequestBuilder` and signs with configured algorithm/provider. `getCertificationRequest` parses PEM input. Builder methods set config, key, subject, cluster/SCM IDs, digital usage flags, CA flag, DNS/IP/service SANs, and host inet addresses.

## Control Flow

Callers configure the builder, `build` validates required key and subject, creates extensions, and returns an immutable request object. Encoding calls `generateCSR`, which adds extension attributes only when present and signs with the private key.

## State and Persistence Behavior

The object holds key pair, config, extensions, subject, cluster ID, and SCM ID in memory. It does not persist files; PEM output is passed over RPC or written by callers.

## Dependencies and Integration Points

It depends on BouncyCastle CSR/ASN.1 APIs, Apache Commons validators, `SecurityConfig`, Ozone certificate exceptions, and `HddsServerUtil.getValidInetsForCurrentHost`. It is used by DN/SCM/default certificate clients and `DefaultApprover`.

## Risks and Edge Cases

Only key and subject are required in `build`; config, SCM ID, and cluster ID can be null until later failures. `getPkcs9Extensions` assumes the extension set exists and has a first element. Domain validation may reject local hostnames. OtherName uses a fixed Microsoft OID.

## Test Signals

Test CSR PEM round-trip, subject/DN formats, key usage flags for signature/encryption/CA, SAN DNS/IP/otherName encoding, missing extension request handling, malformed PEM, missing required builder fields, and generated CSR signature verification.
