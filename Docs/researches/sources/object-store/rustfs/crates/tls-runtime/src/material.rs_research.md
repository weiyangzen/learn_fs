## sources/object-store/rustfs/crates/tls-runtime/src/material.rs

Purpose: loads complete TLS material snapshots from a `TlsSource`, combining server certificate material, outbound root CA bundle, optional client mTLS identity, and a fingerprint that covers all loaded inputs.

Important APIs/types/functions: `OutboundTlsMaterial` stores combined root CA PEM and optional `MtlsIdentityPem`. `ServerTlsMaterial` is either `SingleCert` or `MultiCert` with domain-to-cert/key pairs. `TlsMaterialSnapshot::load(source)` validates the source directory, loads server material, reads public CA and fallback/client CA files, validates client cert/key PEM when both exist, and computes `TlsFingerprint`. Helpers include `load_server_material`, `combine_optional_pem`, and deterministic `serialize_server_material_for_fingerprint`.

Control flow and state: server loading first attempts directory discovery. Multi-cert is selected when more than one cert or any non-default domain exists; a single default cert becomes `SingleCert`; no certs becomes `None`. Public CA and fallback CA PEM are concatenated with newline normalization. Client mTLS identity is present only when both client cert and key files can be read and parsed.

Dependencies and integration points: used by the shared coordinator, outbound global publisher, server resolver, and debug status. Depends on certificate loading helpers, `rustfs_common::MtlsIdentityPem`, rustls PKI types, Tokio file reads, and SHA fingerprints.

Risks: partial client identity files are silently treated as absent unless both reads succeed, except parse errors after both are present; this may hide a missing key/cert misconfiguration. Private key bytes are included in fingerprint input. Server material loading can downgrade some discovery failures to single-root loading or none depending on error kind.

Test signals: covered indirectly by coordinator/server/certs/lib tests. Direct tests for CA bundle concatenation and partial mTLS absence would improve confidence.
