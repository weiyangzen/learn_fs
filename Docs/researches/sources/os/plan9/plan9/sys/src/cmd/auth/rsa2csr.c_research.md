# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2csr.c

Generates an X.509 certificate signing request from an RSA private key. It takes a subject string and optional key file, loads the key with `getkey(..., needprivate=1)`, calls `X509req`, and writes DER output.

Installs mpint and hex formatters for diagnostics/output support.
