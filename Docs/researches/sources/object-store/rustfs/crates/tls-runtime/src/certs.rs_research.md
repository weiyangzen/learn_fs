## sources/object-store/rustfs/crates/tls-runtime/src/certs.rs

Purpose: centralizes certificate/key loading, mTLS client verifier construction, certificate directory inspection, multi-domain certificate discovery, and rustls SNI resolver creation.

Important APIs/types/functions: `CertDirectoryLoadOptions` and builder define directory plus cert/key filenames. `WebPkiClientVerifierOptions` and builder configure optional mTLS verification and fallback CA filenames. `load_certs`, `load_cert_bundle_der_bytes`, and `load_private_key` parse PEM files. `build_webpki_client_verifier` builds a rustls `WebPkiClientVerifier` from client CA bundle when enabled. `TlsCertPairStatus`, `TlsCertPairInspection`, `TlsDomainInspection`, and `TlsDirectoryInspection` model inspection results. `inspect_cert_directory` reports root/domain cert status. `load_all_certs_from_directory` loads root default cert and valid domain certs. `create_multi_cert_resolver` builds an SNI resolver with default fallback.

Control flow and state: directory scanning skips non-directories and hidden/Kubernetes projection-style directories beginning with `.`. Domain pairs are sorted for stable inspection. Loading warns and skips invalid root/domain pairs, but returns `NotFound` if no valid pair exists. Resolver construction maps `"default"` to fallback and other domain names into rustls SNI.

Dependencies and integration points: used by server TLS material loading, target TLS validation, reloadable server cert resolver, and mTLS server verifier setup. Depends on rustls, rustls-pki-types PEM readers, filesystem IO, tracing, and `RootCertStore`.

Risks: many operations are synchronous filesystem reads/parses. `create_multi_cert_resolver` requires private keys supported by the configured rustls crypto provider. Inspection validates parseability but not certificate expiration or hostname correctness. Hidden directory skipping is important for Kubernetes secrets; changing it could accidentally load projection internals.

Test signals: tests cover error construction, missing cert/key file errors, empty directory failure, skipping Kubernetes projection dirs, valid root/domain inspection, and invalid/missing pair reporting.
