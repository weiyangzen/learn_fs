# File Research: sources/os/linux/linux/fs/lockd/svcxdr.h

## Purpose
`svcxdr.h` provides inline helpers for encoding and decoding basic NLM service XDR primitives used by lockd server XDR code.

## Main Responsibilities
- Decode and encode NLM status values.
- Decode bounded caller strings.
- Decode and encode NLM cookies with Linux's smaller `NLM_MAXCOOKIELEN` limit.
- Decode and encode owner handles as XDR opaque netobjs.

## Key Behavior
- `svcxdr_decode_stats()` and `svcxdr_encode_stats()` read/write one XDR unit.
- `svcxdr_decode_string()` enforces `NLM_MAXSTRLEN` and returns a pointer into the XDR stream.
- `svcxdr_decode_cookie()` enforces `NLM_MAXCOOKIELEN`; for a zero-length cookie, it synthesizes a 4-byte zero cookie for HPUX compatibility.
- `svcxdr_encode_cookie()` writes the cookie length then reserves/copies opaque bytes.
- `svcxdr_decode_owner()` enforces `XDR_MAX_NETOBJ` and returns stream-backed owner bytes.
- `svcxdr_encode_owner()` writes owner opaque data and rejects oversized owners.

## Integration Points
- Included by `xdr.c` for legacy NLM server decoding/encoding.
- Shares constants and structures from lockd headers and SUNRPC XDR stream APIs.

## Risks and Edge Cases
- Decoded strings and owners point into the RPC receive buffer, so consumers must not outlive that request buffer unless they copy data.
- Cookie support intentionally differs from the full protocol maximum by limiting cookies to 32 bytes.
