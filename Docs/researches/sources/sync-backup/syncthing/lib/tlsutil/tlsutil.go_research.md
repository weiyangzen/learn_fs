# sources/sync-backup/syncthing/lib/tlsutil/tlsutil.go

Purpose: central TLS configuration, certificate generation, and listener protocol-detection helpers.

Important APIs and control flow: `SecureDefaultTLS13` returns TLS 1.3-only config with a disabled-size client session cache. `SecureDefaultWithTLS12` returns TLS 1.2+ config with a copied curated cipher-suite list, server cipher preference, and HTTP/2/HTTP/1.1 protos. `generateCertificate` creates either browser-compatible ECDSA P-256 or sync-oriented Ed25519 self-signed certs, with CN/DNS name, Syncthing org fields, server/client auth, and day-truncated validity. `NewCertificate` writes PEM cert/key files and returns parsed key pair; `NewCertificateInMemory` avoids filesystem. `DowngradingListener.AcceptNoWrapTLS` accepts a connection, reads one byte with a one-second deadline, wraps it in `UnionedConnection`, and classifies TLS by first byte `0x16`; `Accept` TLS-wraps classified TLS connections. `pemBlockForKey` supports RSA, ECDSA, and Ed25519.

State and persistence: certificate file writes use 0600 for keys; listener state wraps underlying net connections.

Dependencies and integration: used by app device certs, GUI certs, upgrade HTTP clients, and mixed HTTP/HTTPS listeners.

Risks: first-byte TLS detection is heuristic. Read errors return the raw connection as identification failure. Cert file write failures after cert creation can leave partial files. Tests cover cipher list and unioned first-byte behavior.
