# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/CertificateApprover.java

## Purpose

`CertificateApprover` defines the policy interface used by an Ozone certificate authority to inspect CSRs and sign certificates.

## Important APIs, Types, and Functions

`inspectCSR(PKCS10CertificationRequest)` returns a `CompletableFuture<Void>` that completes normally when the CSR is acceptable. `sign(SecurityConfig, PrivateKey, X509Certificate, Date, Date, PKCS10CertificationRequest, String, String, String)` returns a signed `X509Certificate`. `ApprovalType` enumerates `KERBEROS_TRUSTED`, `MANUAL`, and `TESTING_AUTOMATIC`.

## Control Flow

The interface separates asynchronous or policy-rich CSR inspection from the synchronous signing operation. CA implementations call inspection before signing and select behavior based on approval type.

## State and Persistence Behavior

No state or persistence is defined here. Implementations may hold profiles, configuration, and policy state.

## Dependencies and Integration Points

It is consumed by `DefaultCAServer` and implemented by `DefaultApprover`. It depends on BouncyCastle PKCS#10 requests, Java private keys/certificates, and `SecurityConfig`.

## Risks and Edge Cases

Manual approval is part of the type contract but not implemented by the default CA. The interface permits asynchronous inspection, so callers must handle exceptional completion correctly.

## Test Signals

Mock approver tests should cover normal and exceptional future completion, manual approval rejection in CA code, and sign parameter propagation including validity dates, serial ID, SCM ID, and cluster ID.
