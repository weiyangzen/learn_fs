# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/httpdigest.c

Implements client-side HTTP Digest MD5 authentication for RFC 2617 style challenge/response. Server mode is explicitly unsupported.

Protocol state is `CNeedChal -> CHaveResp -> Established`. On write, it finds a matching key with `user`, `realm`, and private `!password`, parses `nonce method uri`, and computes `MD5(HA1:nonce:HA2)` as lowercase hex. On read, it returns the stored digest response.

Key prompt is `user? realm? !password?`; `addkey` uses `replacekey`. Dependencies include MD5, attr/key matching, and factotum phase/error helpers.
