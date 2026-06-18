# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/authority/DefaultCAServer.java

## Purpose

`DefaultCAServer` is the default SCM certificate authority implementation. It bootstraps or validates CA key/certificate files, supports external or self-signed root CA initialization, signs CSRs through `DefaultApprover`, stores issued certificates, and exposes CA certificate lookup/listing APIs.

## Important APIs, Types, and Functions

Constructors set subject, cluster ID, SCM ID, `CertificateStore`, root cert ID, profile, and component name. `init` resolves certificate location, builds `DefaultApprover`, verifies key/cert state, and runs the selected initializer. `requestCertificate` inspects CSR, rejects manual approval, signs/stores automatic requests, and prepends the signed cert to CA cert path. `signAndStoreCertificate` computes validity, locks issuance, checks serial ID, signs, and stores. `processVerificationStatus` maps `SUCCESS`, `MISSING_KEYS`, `MISSING_CERTIFICATE`, and `INITIALIZE` to actions. Root initialization uses `HDDSKeyGenerator`, `KeyStorage`, `SelfSignedCertificate`, and `CertificateCodec`.

## Control Flow

Startup follows a truth table over key and certificate presence. Issuance follows inspect, choose approval mode, sign under lock, persist, build returned cert chain. Root CA initialization either imports an external certificate or generates keys and a self-signed CA certificate.

## State and Persistence Behavior

The server stores configuration, approver, profile, certificate store, component paths, and a lock. Durable state lives in key files, certificate files, and `CertificateStore`. Issued certificate storage is serialized by the lock.

## Dependencies and Integration Points

It integrates SCM metadata DB, `CertificateStore`, `SecurityConfig`, `CertificateCodec`, `KeyStorage`, `HDDSKeyGenerator`, `SelfSignedCertificate`, BouncyCastle CSR handling, and protobuf `NodeType`.

## Risks and Edge Cases

Missing keys with present certs and missing certs with present keys are fatal except external root import. `requestCertificate` checks exceptional CSR futures by calling `get`, but the following signing block is still reachable unless the future handling completes exceptionally first. Null `store` is tolerated for signing but disables persistence. Root CA external import logs errors rather than throwing, leaving success validation to the final status check.

## Test Signals

Tests should cover all verification statuses, external root CA import, self-signed root generation, subordinate initialize failure, manual approval rejection, CSR inspection failure, duplicate serial rejection, role-based duration selection, store reinitialization, and cert chain ordering.
