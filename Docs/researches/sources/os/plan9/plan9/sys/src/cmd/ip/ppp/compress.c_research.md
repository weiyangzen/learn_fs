# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ppp/compress.c

Implements Van Jacobson TCP/IP header compression and decompression for PPP.

Key behavior:
- `compress_init` initializes transmit/receive header state arrays.
- `compress` filters to non-fragmented IPv4 TCP packets and delegates to `tcpcompress`.
- `tcpcompress` finds or allocates a connection state, validates invariant IP/TCP header fields, encodes deltas for urgent pointer, window, ack, seq, IP ID, and special interactive/data cases, or sends uncompressed state refresh.
- `tcpuncompress` restores headers from compressed or uncompressed VJ packets, tracks missing explicit connection IDs after line errors, updates IP checksum, and frees bad packets.
- `compress_negotiate` validates peer state count and stores whether connection IDs are compressed.
- `compress_error` marks receive state invalid after a bad PPP frame.

Integration points:
- Used by `pppwrite` and `pppread` when IPCP negotiates `Fipcompress`.
- Uses `Block` helpers, `ipcsum`, and PPP protocol constants `Pvjctcp`, `Pvjutcp`, `Pip`.

Risks and notes:
- Only TCP is compressed; other IP protocols remain plain.
- Decompression assumes enough front padding for reconstructed headers, with fallback through `padb`/`pullup`.
