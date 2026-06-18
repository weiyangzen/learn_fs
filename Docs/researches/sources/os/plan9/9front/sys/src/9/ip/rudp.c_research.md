# File Research: sources/os/plan9/9front/sys/src/9/ip/rudp.c

Implements 9front’s reliable UDP-like protocol over IPv4 protocol number 254.

Key elements:
- Uses UDP-compatible port fields plus a reliability header containing sequence, generation, ack, and ack-generation fields.
- Maintains per-peer `Reliable` state for send sequence, receive sequence, unacked queue, retransmits, and flow control.
- Starts an ack/retransmit kernel process lazily.
- Provides connect/announce, header mode, randdrop testing, and per-peer hangup control.
- Sends delayed acks, retransmits unacked packets, and tears down state after repeated failures.
- Supports header mode that passes remote/local/interface addresses and ports to user space.

Dependencies:
- Uses IPv4 output, ICMP no-conversation reporting, IP hash tables, and Plan 9 queues.
- Uses shared source-address helpers from the IP interface layer.

Research notes:
- Despite using IPv6-sized internal addresses, the wire protocol is IPv4-only.
- Generations distinguish restarted peers and avoid accepting stale acknowledgements.
- Flow control blocks writers when more than `Maxunacked` packets are outstanding.
