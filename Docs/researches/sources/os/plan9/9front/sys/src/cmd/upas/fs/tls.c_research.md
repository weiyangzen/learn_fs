# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/tls.c

This file wraps a connected fd in TLS and validates server certificates for mail protocols.

Key behavior:
- Calls `tlsClient` with `serverName`.
- If global `nocertcheck` is set, logs that cert checking is ignored and returns the TLS fd.
- Otherwise loads thumbprints from `/sys/lib/tls/mail` and exclusion list `/sys/lib/tls/mail.exclude`.
- Validates the server cert with `okCertificate`; on failure closes TLS fd and returns `-1`.
- Frees TLS certificate/session resources.

Integration and risks:
- Used by IMAP and POP backends.
- Trust is thumbprint-file based rather than CA-chain based.
