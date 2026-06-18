# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2pub.c

RSA key public-half extractor.

Key responsibilities:
- Reads a Plan 9 RSA key.
- Preserves residual non-key attributes.
- Prints a factotum-style public key line with `size`, `ek`, and `n`.

Dependencies:
- Uses `getrsakey`, auth attribute formatting, and mpint formatting.
