## sources/object-store/rustfs/crates/tls-runtime/src/fingerprint.rs

Purpose: provides the shared SHA256 fingerprint structure used to detect TLS material changes across server, outbound CA, client CA, and mTLS identity inputs.

Important APIs/types/functions: `TlsFingerprint` contains optional digests for `server_sha256`, `public_ca_sha256`, `client_ca_sha256`, `client_cert_sha256`, and `client_key_sha256`. `from_optional_bytes` digests each supplied byte slice and leaves absent inputs as `None`. Private `digest_bytes` wraps `sha2::Sha256`.

Control flow and state: pure deterministic hashing with no IO and no mutable state.

Dependencies and integration points: used by `TlsMaterialSnapshot`, target TLS fingerprint helper, server resolver fingerprinting, and reload coordinators for equality checks.

Risks: fingerprints include private key bytes for change detection; they are only digests, but code paths handling them should still avoid leaking debug representations unnecessarily. Domain ordering must be stabilized before hashing multi-cert material, which `material` and `server` handle explicitly.

Test signals: crate-level tests verify fingerprint changes when server material changes; server resolver tests verify stable fingerprints across domain ordering.
