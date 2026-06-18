# File Research: sources/os/bsd/netbsd-src/lib/libc/inet/inet_ntoa.c

Implements legacy `inet_ntoa`.

Behavior:
- Uses a static 18-byte buffer initialized to `"[inet_ntoa error]"`.
- Calls `inet_ntop(AF_INET, &in, ret, sizeof ret)` to produce dotted decimal output.
- Returns the static buffer.

Not thread-safe due to static storage, matching traditional `inet_ntoa` semantics.
