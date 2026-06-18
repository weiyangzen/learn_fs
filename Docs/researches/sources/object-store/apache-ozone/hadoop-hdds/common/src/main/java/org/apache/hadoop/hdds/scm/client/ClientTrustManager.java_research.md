# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/client/ClientTrustManager.java

## Purpose
Implements a refreshable client-side `X509ExtendedTrustManager` for gRPC and Ratis clients. It starts from in-memory CA certificates and refreshes from a remote provider when server certificate validation fails, supporting CA rotation for long-lived clients.

## Important APIs, Types, And Functions
Constructor accepts remote and in-memory `CACertificateProvider` instances and requires at least one. `initialize(List<X509Certificate>)` builds a `KeyStore` and delegates to `TrustManagerFactory`. `checkServerTrusted` overloads delegate and retry once after remote reload. `checkClientTrusted` overloads reject server-side use.

## Control Flow
On construction, certs are loaded and a delegate trust manager is selected. During server verification, a certificate failure logs, reloads certificates from the remote provider, reinitializes the delegate, and retries verification.

## State And Persistence
State is an in-memory delegate trust manager and providers. No keystore is written to disk; each reload builds an ephemeral keystore keyed by certificate serial number.

## Dependencies And Integration Points
Depends on Java SSL APIs and HDDS `CACertificateProvider`. Integrated by client factories that connect to SCM/OM/datanode endpoints with TLS and CA rotation.

## Risks And Test Signals
Remote provider security is critical because failed validation triggers trust-root refresh. The delegate field is not synchronized during reload. Tests should cover initial load, null provider combinations, refresh on failure, accepted issuers after reload, and rejection of client-trust methods.
