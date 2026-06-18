# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/x509/certificate/client/CACertificateProvider.java

## Purpose
Functional interface for supplying trusted CA certificates.

## Important APIs and types
`provideCACerts()` returns a `List<X509Certificate>` and can throw `IOException`.

## Control flow and state
No implementation state exists. Implementations decide whether certificates come from disk, SCM, memory, or another service.

## Dependencies and integration points
Certificate clients and TLS/trust-store setup code can depend on this interface without knowing certificate source details.

## Risks and test signals
Tests for consumers should cover provider IO failure, empty certificate lists, and multiple CA certificates. Implementations should document ordering expectations.
