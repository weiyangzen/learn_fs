# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateServer.java

## Purpose

`CertificateServer` is the abstraction for an SCM certificate authority. It allows the default in-process CA to be replaced later by external CAs or HSM-backed implementations.

## Important APIs, Types, and Functions

The interface defines `init(SecurityConfig, CAType)`, `getCACertificate()`, `getCaCertPath()`, `getCertificate(String)`, `requestCertificate(PKCS10CertificationRequest, ApprovalType, NodeType, String)`, `listCertificate(NodeType, long, int)`, and `reinitialize(SCMMetadataStore)`.

## Control Flow

Consumers initialize the CA, retrieve CA material, request issued certificates through CSR approval/signing, list stored certificates, and reinitialize the backing store after SCM metadata reload.

## State and Persistence Behavior

Persistence is delegated to implementations and their `CertificateStore`. The interface makes certificate issuance and listing part of the persistent CA contract.

## Dependencies and Integration Points

It bridges HDDS security configuration, SCM metadata store, BouncyCastle CSR objects, protobuf `NodeType`, Java `CertPath`, and `X509Certificate`.

## Risks and Edge Cases

`requestCertificate` returns `Future<CertPath>`, so implementations can be asynchronous and callers must handle delayed exceptional failure. `getCertificate` returns null for absent certificates in the default implementation, so null checks are required.

## Test Signals

Contract tests should cover successful initialization, missing certificate lookup, request failure propagation, certificate path ordering, role-based listing, and store reinitialization.
