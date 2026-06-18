# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2pub.c

Converts an RSA key line to a public-only factotum key line. It preserves non-key attrs, emits `size`, `ek`, and `n`, and omits private fields.

Uses `getkey(..., needprivate=0)` so it can process public or private input.
