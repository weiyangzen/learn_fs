# File Research: sources/os/plan9/9front/sys/src/9/ip/il.c

Implements IL, Plan 9’s reliable datagram protocol over IPv4, using IP protocol number 40. It provides connection setup, sequencing, acknowledgments, retransmission, out-of-order buffering, close handling, and adaptive timeout estimates.

Key responsibilities:
- Registers protocol `il`.
- Connects/listens through `ilconnect()` and `ilannounce()`.
- Sends data through `ilkick()` with IL/IP headers and sequence numbers.
- Receives packets through `iliput()` and state machine processing in `ilprocess()`.
- Maintains unacknowledged and out-of-order queues.
- Runs periodic ack/retransmit/query handling in `ilackproc()`.
- Handles ICMP advice in `iladvise()`.

Important implementation details:
- `Ilcb` stores state, sequence counters, receive window, retransmission counters, timers, RTT/rate estimates, and queues.
- State machine covers `Ilclosed`, `Ilsyncer`, `Ilsyncee`, `Ilestablished`, `Illistening`, `Ilclosing`, and `Ilopening`.
- Packet types include sync, data, dataquery, ack, query, state, and close.
- Outbound data is copied to an unacked queue so it can be retransmitted.
- `ilpullup()` delivers in-order data to the read queue and frees duplicates.
- Query/state packets support selective retransmission decisions through small query timestamp table `qt`.
- `fasttimeout` can be requested by appending `!fasttimeout` to connect arguments.

Dependencies and integration:
- Uses `Fsstdconnect`, `Fsstdannounce`, `Fsnewcall`, and `Fsconnected`.
- Uses `Ipht` to match incoming packets to conversations/listeners.
- Sends through `ipoput4()` only; connect rejects non-IPv4.
- Uses `ptclcsum()` for IL checksums.

Research notes:
- IL is IPv4-only here.
- The ack worker is started lazily per protocol instance.
- Queue limits protect mount RPC buffer pressure by dropping data when the read queue reaches `Maxrq`.
