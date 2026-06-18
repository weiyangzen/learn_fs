<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tofu.go -->
# sources/object-store/minio-mc/cmd/tofu.go

Purpose: implements trust-on-first-use handling for self-signed TLS certificates, prompting the user to trust a server certificate and saving it in the local CA directory.

Important APIs/types/functions: `marshalPublicKey`, `promptTrustSelfSignedCert`, and `fetchPeerCertificate`.

Control flow: `promptTrustSelfSignedCert` skips HTTP endpoints, then attempts an HTTPS request using loaded root CAs. If the request succeeds, nothing is needed. If the failure is an unknown/untrusted authority, it fetches the peer cert with `InsecureSkipVerify`, verifies that the certificate is self-signed using subject/authority key IDs or a SHA-1 public-key check for self-CA certs, prints the SHA-256 public-key fingerprint, and asks for `y/yes`. On confirmation, it writes `<alias>.crt` to `mustGetCAsDir`.

State and persistence: persists trusted certificates as PEM files in the mc CAs directory. Reads from stdin for confirmation.

Dependencies and integration points: uses custom TLS dialing, global root CAs, config directory helpers, probe errors, and standard x509/asn1 handling for RSA/ECDSA/Ed25519 public keys.

Risks and test signals: interactive trust prompts are security-sensitive. Tests should cover HTTP bypass, already trusted certs, non-self-signed unknown cert rejection, fingerprint confirmation rejection, PEM write errors, and public-key marshal variants.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tofu.go -->
