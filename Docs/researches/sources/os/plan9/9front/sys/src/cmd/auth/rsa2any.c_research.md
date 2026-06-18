# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.c

Shared RSA key parser and binary encoding helpers for RSA conversion commands.

Key responsibilities:
- Reads a Plan 9 factotum-style `key proto=rsa ...` line from a file or stdin.
- Parses public fields `ek`, `n`, and optional/corrected `size`.
- Optionally requires and parses private fields `!dk`, `!p`, `!q`, `!kp`, `!kq`, `!c2`.
- Regenerates missing or bad CRT fields with `rsafill`.
- Removes RSA numeric/private fields from the returned residual attribute list.
- Provides SSH-style helpers for big-endian 4-byte lengths, strings, raw bytes, and mpints.

Dependencies:
- Uses Plan 9 auth attribute parser, libmp/libsec RSA helpers, and `rsa2any.h`.

Notable risks:
- Error paths do not uniformly free all partial allocations, acceptable for short-lived conversion tools.
