# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2ssh.c

Converts a DSA key to OpenSSH public key format.

Key points:
- Reads a DSA private key with `getdsakey`.
- Serializes SSH wire fields: algorithm name `ssh-dss`, p, q, alpha, and public key.
- Prints base64-encoded public key and optional comment.

Dependencies:
- Uses `rsa2any.h` helpers `put4`, `putn`, and `putmp2`.

Notable behavior:
- Supports `-c comment`.
