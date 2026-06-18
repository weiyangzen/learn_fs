# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_http.c

HTTP-backed address-list loader.

Key behavior:
- Accepts `http://` URLs up to 512 bytes.
- Sends a simple HTTP/1.0 GET with `Host:` header over `connecttcp()`.
- Requires a 2xx status line.
- Strips headers, then parses body lines like `load_file()`: comments, whitespace trimming, and `alist_new()` entries.

Research notes:
- Explicitly avoids truncating oversized URLs.
- Header/body buffer compaction is manual and sensitive to off-by-one mistakes.
