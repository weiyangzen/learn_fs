# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/httpdigest.c

Factotum client-side HTTP Digest response generator for RFC 2617-style MD5 digest auth.

Key responsibilities:
- Supports client role only; server role returns unsupported.
- Accepts challenge data as `nonce method uri`.
- Finds a key with `user`, `realm`, and private `!password`.
- Computes `MD5(HA1:nonce:HA2)` with lowercase hex encoding.
- Returns the digest response and marks authentication established without `AuthInfo`.

Dependencies:
- Uses factotum key lookup, attribute handling, tokenize, MD5, and hex encoding.

Notable risks:
- Only the older/simple digest formula is implemented; no qop/cnonce/nc support is present.
