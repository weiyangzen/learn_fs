# File Research: sources/os/plan9/plan9/sys/src/9/ip/tcp.c

## Purpose
Implements Plan 9's TCP protocol for IPv4 and IPv6. It provides connection setup/teardown, data transfer, retransmission timers, delayed ACKs, keepalives, congestion control, resequencing, SYN-flood limbo handling, protocol stats, and the Plan 9 IP `Proto` interface.

## Main Data Structures
- `Tcp4hdr` / `Tcp6hdr`: pseudo-header plus TCP header layouts used for checksum and packet construction.
- `Tcp`: normalized per-segment metadata decoded from packet headers and encoded back to headers.
- `Tcpctl`: per-conversation TCP control block. Tracks state, send/receive sequence variables, windows/scaling, congestion window, slow-start threshold, RTT estimators, timers, keepalive counters, resequencing queue, and protocol header templates.
- `Tcptimer`: linked-list timer entry driven by the protocol timer kproc.
- `Reseq`: queued out-of-order segment with associated `Block`.
- `Limbo`: half-open listener-side SYN/SYN-ACK state held outside normal conversations to reduce SYN attack pressure.
- `Tcppriv`: protocol-global timer list, conversation hash table, limbo hash table, kproc startup state, and stats.

## Connection Lifecycle
- `tcpinit` registers the TCP protocol with `Fsproto`, using `scalednconv()` for maximum conversations.
- `tcpconnect` validates closed state, performs standard connect setup, then calls `tcpstart(..., TCP_CONNECT)`.
- `tcpannounce` performs standard announce setup, then starts a listening TCP control block.
- `tcpstart` starts the timer kproc if necessary, initializes the TCB, adds the conversation to the IP hash table, and either enters `Listen` or sends a SYN and enters `Syn_sent`.
- `tcpclose` maps local close to state-machine transitions: immediate local close for listening/closed/syn-sent, FIN transmission for established states, and `Last_ack` from `Close_wait`.
- `localclose` removes the conversation from the hash table, stops timers, dumps resequencing state, wakes listeners/connect waiters as needed, hangs up queues, and moves to `Closed`.

## Packet Input
- `tcpiput` detects IPv4 versus IPv6, verifies checksum, parses TCP options, trims the packet to the declared payload, looks up the conversation, and handles listener limbo cases.
- Listener SYNs are placed in `Limbo` via `limbo`; matching final ACKs are promoted to a new conversation via `tcpincoming`.
- The state-machine logic handles `Closed`, `Syn_sent`, `Syn_received`, established transfer states, FIN states, `Time_wait`, RSTs, ACK validation, urgent-pointer bookkeeping, data queueing, FIN processing, and forced ACK decisions.
- `tcptrim` enforces receive-window acceptance, trims duplicates at the left edge and excess at the right edge, and clears SYN/FIN/URG as appropriate.
- Out-of-order data is queued by `addreseq`; adjacent queued segments are later pulled with `getreseq`.

## Packet Output
- `tcpoutput` sends up to 100 packets per pass, applying delayed-ACK rules, window opening ACKs, zero-window probes, congestion window, advertised send window, MSS limit, SYN/SYN-ACK option generation, PSH/FIN flags, and per-version header/checksum construction.
- `htontcp4` and `htontcp6` build wire packets and encode MSS/window-scale options on SYN packets.
- `ntohtcp4` and `ntohtcp6` parse incoming header length, flags, window, urgent pointer, payload length, MSS, and window-scale options.
- `sndrst` and `tcphangup` generate reset packets and close local state.

## Timers and Reliability
- `tcpackproc` is the global timer kproc. It ticks every `MSPTICK`, advances active timers, invokes ready callbacks, and calls `limborexmit`.
- `tcpsettimer` derives retransmit timeout from smoothed RTT, mean deviation, and exponential backoff, clamped between 300 ms and 64 s.
- `tcptimeout` handles retransmission timeout, congestion response, recovery reset, and eventual timeout close.
- `tcprxmit` retransmits one segment at `snd.una` while preserving the normal send pointer and congestion window.
- `tcpsynackrtt` and `update` maintain RTT estimates from SYN/SYN-ACK and later acknowledged full-MSS packets.
- `tcpkeepalive`, `tcpsendka`, and `tcpstartka` implement BSD-style keepalives and optional port-hog defense probes.

## Congestion and Flow Control
- Implements slow start and congestion avoidance with appropriate byte counting (`tcpabcincr`).
- Implements NewReno-style fast retransmit/recovery with duplicate ACK threshold, recovery window inflation/deflation, partial ACK handling, and RTO recovery counters.
- Supports RFC 1323-style window scaling. `tcpsetscale` configures queue limits, receive scaling, send scaling, and receive window size while bounding local queue commitment with `Maxqscale`.
- `tcprcvwin` calculates receive window from queue occupancy and avoids moving the right edge backward.

## Control and Observability
- Control commands:
  - `hangup`: send RST and close.
  - `keepalive [ms]`: enable keepalives for established connections.
  - `checksum n`: toggles outgoing checksum behavior.
  - `tcpporthogdefense on|off`: toggles stateless port-hog defense.
- `tcpstate` reports TCP state, queue lengths, resequencing size, RTT state, congestion/window values, timers, and rereceive bytes.
- `tcpstats` prints MIB and non-MIB counters including opens, resets, segment counts, checksum/header/length errors, resequencing limits, delayed ACKs, and recovery statistics.
- `tcpgc` opportunistically closes stale `Syn_received` and long-lived `Finwait2` conversations when channel pressure occurs.

## Dependencies and Integration
Integrates with Plan 9 IP hash tables, queues, block buffers, ICMP advice, IPv4/IPv6 output, timers, locks, and filesystem connection management. It depends on common IP helpers for local address selection, protocol checksum, packet output, and conversation allocation.

## Risks and Notes
This is a complete in-kernel TCP implementation with many coupled state transitions. Notable edge areas include overflow-sensitive RTT calculations, resequencing queue limits tied to receive window and MSS, limbo list linear scans, optional checksum disabling, and hardware/offload checksum flag interaction via `Btcpck`.
