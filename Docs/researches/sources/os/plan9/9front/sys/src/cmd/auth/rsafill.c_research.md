# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsafill.c

RSA private-key normalizer that fills missing CRT fields.

Key responsibilities:
- Reads a private Plan 9 RSA key.
- Uses shared parser, which regenerates missing/bad `!kp`, `!kq`, and `!c2`.
- Prints a full factotum-style private key line with size, public fields, and private CRT fields.

Dependencies:
- Uses `getrsakey`, auth attribute formatting, and mpint formatting.
