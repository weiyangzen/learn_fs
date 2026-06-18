# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2csr.c

RSA certificate signing request generator.

Key responsibilities:
- Reads a private RSA key.
- Accepts a subject string such as `C=US ... CN=...`.
- Calls `X509rsareq` to create a DER CSR.
- Writes the CSR bytes to stdout.

Dependencies:
- Uses `getrsakey`, libsec X.509 request generation, and mp/hex formatters.
