<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go -->
# sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go

- Purpose: Tests generated TLS certificates and fingerprint-based trust transport.
- Important APIs/types/functions: `TestGenerateServerCertificate`, `TestTransportTrustingSingleCertificate`.
- Control flow: Generates certs with IP/DNS names, checks SANs and validity window, computes SHA256 fingerprint, obtains a transport, and directly invokes `VerifyPeerCertificate` for matching and mismatching raw certs.
- State and persistence: Uses in-memory certificates only; file writing helpers are not covered.
- Dependencies and integration points: Uses `clock`, `crypto/sha256`, `http.Transport`, and `testify/require`.
- Risks and edge cases: Does not perform a real TLS handshake or test PEM file permissions.
- Test signals: Direct coverage for core TLS utility behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go -->
