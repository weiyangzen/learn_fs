# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2ssh.c

RSA public key converter to OpenSSH authorized-key format.

Key responsibilities:
- Reads a public RSA key.
- Packs SSH wire fields: string `ssh-rsa`, exponent, modulus.
- Base64-encodes the packed key.
- Supports optional `-c comment`.
- Accepts `-2` for backwards compatibility.

Dependencies:
- Uses `getrsakey`, `put4`, `putn`, `putmp2`, and Plan 9 base64 formatter.
