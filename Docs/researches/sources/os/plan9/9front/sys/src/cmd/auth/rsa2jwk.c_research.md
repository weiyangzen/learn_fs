# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2jwk.c

RSA public key converter to JSON Web Key format.

Key responsibilities:
- Reads a public RSA key.
- Encodes modulus and exponent as base64url without padding.
- Prints a minimal JSON object with `kty`, `n`, and `e`.

Dependencies:
- Uses `getrsakey`, mpint big-endian conversion, and custom base64url character mapping.
