# File Research: sources/os/plan9/9front/sys/src/9/ip/tcp.c

Implements the TCP protocol for IPv4 and IPv6.

Key elements:
- Defines TCP wire pseudo-headers, segment metadata, resequencing queue entries, timers, limbo SYN state, and per-connection control blocks.
- Implements active open, passive open, close, hangup, keepalive, state reporting, and garbage collection.
- Uses SYN limbo entries to avoid allocating full conversations before SYN-ACK completion.
- Handles TCP options for MSS and window scale.
- Implements checksum validation and header parsing for IPv4 and IPv6.
- Runs the TCP state machine for SYN, ACK, RST, FIN, receive trimming, delayed ACKs, and close states.
- Implements output segmentation, send-window checks, receive-window updates, retransmission timers, RTT estimation, keepalive probes, and zero-window probes.
- Includes NewReno-style fast retransmit/recovery and appropriate byte counting.
- Supports local TCP splicing by bypassing queues between two local established conversations.
- Supports transparent forwarding/NAT hooks and MSS clamping for forwarded SYN packets.
- Exposes detailed TCP stats.

Dependencies:
- Uses `iproute.c` for route hints/source selection, `ipifc.c` for local address selection, IPv4/IPv6 output paths, IP hash tables, translation helpers, and queues.

Research notes:
- The implementation deliberately avoids allocating full `Conv` state for half-open passive connections until the final ACK arrives.
- IPv6 MSS defaults to 1220 unless route/interface conditions justify a larger value.
- Timers are maintained by a protocol kernel process that also retransmits limbo SYN-ACKs.
