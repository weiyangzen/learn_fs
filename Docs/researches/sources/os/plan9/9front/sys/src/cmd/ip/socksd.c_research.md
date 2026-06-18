# File Research: sources/os/plan9/9front/sys/src/cmd/ip/socksd.c

This is a SOCKS4/SOCKS4a/SOCKS5 proxy server for Plan 9 network files.

Key behavior:
- Supports `CONNECT`, `BIND`, and SOCKS5 `UDP ASSOCIATE`.
- Accepts SOCKS5 “no authentication” only.
- Converts between SOCKS address encodings and Plan 9 dial strings.
- Provides UDP relay using Plan 9 UDP header mode and forked bidirectional forwarding.
- Supports `-x` and `-o` to choose inside/outside network mount points.

Research notes:
- SOCKS4a domain parsing is implemented.
- The program relies on Plan 9 `announce`, `listen`, `accept`, `dial`, and network connection metadata.
