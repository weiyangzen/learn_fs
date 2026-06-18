# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsagen.c

RSA private key generator.

Key responsibilities:
- Generates RSA keys with default 2048 bits or `-b bits`.
- Loops until modulus bit length matches the requested size.
- Supports `-t` to add arbitrary factotum key attributes.
- Prints a factotum-style `key proto=rsa ...` private key line.

Dependencies:
- Uses libsec `rsagen`, mpint formatting, and Plan 9 I/O.
