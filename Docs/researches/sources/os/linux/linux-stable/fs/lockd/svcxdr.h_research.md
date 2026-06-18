# File Research: sources/os/linux/linux-stable/fs/lockd/svcxdr.h

## Summary
Inline helpers for common server-side NLM XDR scalar, cookie, string, and owner-handle encoding/decoding.

## Main APIs
`svcxdr_decode_stats()`, `svcxdr_encode_stats()`, `svcxdr_decode_string()`, `svcxdr_decode_cookie()`, `svcxdr_encode_cookie()`, `svcxdr_decode_owner()`, and `svcxdr_encode_owner()`.

## Behavior
Strings are bounded by `NLM_MAXSTRLEN`. Cookies are specified as up to 1024-byte XDR opaque values, but Linux caps them at `NLM_MAXCOOKIELEN` and maps zero-length HPUX cookies to four zero bytes. Owner handles are bounded by `XDR_MAX_NETOBJ` and generally point directly into the decoded XDR buffer.

## Dependencies
SunRPC `xdr_stream`, `nlm_cookie`, `xdr_netobj`, and lockd constants from `xdr.h`.

## Risks
Decoded string and owner storage aliases the RPC receive buffer, so callers must not outlive the request unless they copy. Cookie length policy is intentionally stricter than the protocol.
