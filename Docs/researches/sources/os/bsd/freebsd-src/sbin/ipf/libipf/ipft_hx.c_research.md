# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/ipft_hx.c

Hexadecimal packet-input backend for IPFilter test tooling.

Key behavior:
- Exports `iphex` as an `ipread` provider with open, close, and packet-read callbacks.
- Reads packet bytes from text hex, ending a packet at a blank line.
- Supports optional leading metadata like `[ifname]` or `[in/out,ifname]`.
- Parses `+mcast`, `+bcast`, and `+mbcast` flags into `mb_t`.

Research notes:
- Maintains static file state and rewinds on repeated opens.
- `ifn` sometimes receives a direct pointer into the local line buffer in the no-direction bracket case, which is fragile after return.
