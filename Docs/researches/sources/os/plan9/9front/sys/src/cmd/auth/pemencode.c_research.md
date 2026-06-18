# File Research: sources/os/plan9/9front/sys/src/cmd/auth/pemencode.c

PEM section encoder.

Key responsibilities:
- Reads all binary input from a file or stdin.
- Base64-encodes it and wraps output in `-----BEGIN <section>-----` / `-----END <section>-----`.
- Emits 64-character base64 lines.

Dependencies:
- Uses libsec base64 encoding.
