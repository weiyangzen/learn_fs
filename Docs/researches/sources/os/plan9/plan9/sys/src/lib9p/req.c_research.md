# File Research: sources/os/plan9/plan9/sys/src/lib9p/req.c

This file manages request pools, request lookup, reference counting, and request destruction.

Key behavior:
- `allocreqpool` creates an `Intmap` keyed by 9P tag with lookup ref increments.
- `allocreq` creates and inserts a `Req`, taking one map reference and one caller reference.
- `lookupreq` returns a referenced request by tag.
- `removereq` removes a request from the pool map.
- `closereq` releases fids, newfids, afids, old flush target refs, delayed flush requests, stat buffers, copied `Dir` strings, custom destroy hook, request buffers, and the request itself.
- `freereqpool` frees the map and applies the configured request destroy hook.

Important dependencies:
- Uses `Intmap` from `intmap.c`.
- Coordinates with flush and response handling in `srv.c`.

Notable details:
- If a request is destroyed while flush requests are queued, `closereq` responds to those flushes with success.
- Debug tracing is gated by `chatty9p > 1`.
