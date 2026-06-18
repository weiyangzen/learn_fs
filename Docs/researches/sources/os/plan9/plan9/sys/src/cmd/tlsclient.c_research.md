# File Research: sources/os/plan9/plan9/sys/src/cmd/tlsclient.c

Simple TLS client wrapper around a dialed network connection.

Key responsibilities:
- Parses optional trusted thumbprint file `-t` and exclusion file `-x`.
- Dials the supplied Plan 9 dialstring.
- Upgrades the connection with `tlsClient`.
- Optionally verifies the server certificate SHA-1 thumbprint.
- Forks bidirectional copy loops between stdin/stdout and the TLS fd.
- Posts a note to the process group when one direction finishes.

Notable behavior:
- `-x` without `-t` is rejected.
- Verification requires the server to provide a certificate.
- Uses Plan 9 libsec thumbprint handling rather than a full PKI validation path.
