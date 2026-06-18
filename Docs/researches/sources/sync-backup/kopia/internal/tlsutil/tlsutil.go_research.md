<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil.go -->
# sources/sync-backup/kopia/internal/tlsutil/tlsutil.go

- Purpose: Provides TLS certificate generation, PEM writing, and single-fingerprint trust helpers.
- Important APIs/types/functions: `GenerateServerCertificate`, `WritePrivateKeyToFile`, `WriteCertificateToFile`, `TLSConfigTrustingSingleCertificate`, `TransportTrustingSingleCertificate`, `verifyPeerCertificate`.
- Control flow: Certificate generation creates RSA key, validity window, random serial, server-auth self-signed cert, and DNS/IP SANs. Write helpers open files mode `0600` and PEM-encode. Trust helpers clone HTTP transport and install fingerprint verification.
- State and persistence: Writes private key/certificate files when requested; otherwise returns in-memory TLS objects.
- Dependencies and integration points: Integrates `crypto/x509`, `tls`, `net/http`, `clock`, and Kopia logging.
- Risks and edge cases: `InsecureSkipVerify` is intentionally used with fingerprint verification; wrong fingerprints reject all certs and normal hostname PKI checks are bypassed.
- Test signals: `tlsutil_test.go` covers cert SAN/validity and fingerprint accept/reject.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil.go -->
