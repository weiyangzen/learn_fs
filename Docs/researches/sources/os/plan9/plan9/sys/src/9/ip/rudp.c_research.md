# File Research: sources/os/plan9/plan9/sys/src/9/ip/rudp.c

## Purpose
Implements Plan 9's Reliable User Datagram Protocol (`rudp`), an IPv4-only reliable datagram protocol using a UDP-compatible packet shape plus a 16-byte reliability header. It registers as protocol number `254` and exposes the standard Plan 9 IP `Proto` interface.

## Main Data Structures
- `Udphdr` and `Rudphdr`: IPv4 pseudo-header plus UDP header, with `Rudphdr` adding reliable sequence, generation, ack, and ack-generation fields.
- `Reliable`: per-peer state keyed by remote IP and port. Tracks send/receive sequence numbers, generations, unacked packet list, retransmit timers, flow-control sleep state, and reference count.
- `Rudpcb`: per-conversation private state containing the peer `Reliable` list plus `headers` and `randdrop` controls.
- `Rudppriv`: protocol global hash table, MIB-like counters, checksum/length/retransmit/out-of-order stats, and ack kproc startup state.

## Protocol Flow
- `rudpinit` allocates and registers the `rudp` protocol with connect, announce, create, close, receive, control, advise, state, and stats callbacks.
- `rudpconnect` and `rudpannounce` start the global ack/retransmit kproc, use `Fsstdconnect`/`Fsstdannounce`, mark the conversation connected, and add it to the protocol hash table.
- `rudpkick` dequeues user data from `wq`, optionally parses user-supplied address headers, constructs IPv4/UDP/RUDP headers, assigns a next send sequence, piggybacks the latest receive ack, computes checksum, stores a retransmission copy through `relackq`, sends with `ipoput4`, and applies simple flow control when `UNACKED(r) > Maxunacked`.
- `rudpiput` validates the UDP checksum, finds a conversation via `iphtlook`, calls `reliput` for reliability state handling, trims off protocol headers, optionally prepends source metadata for `headers`, then queues payload to `rq`.
- `relackproc` wakes every `Rudptickms`, retransmits peers whose first unacked packet has timed out, and sends delayed ACK-only packets when needed.
- `reliput` handles ack validation by generation, hangup packets, receive-generation changes, unacked queue advancement, flow-control wakeups, duplicate/out-of-order rejection, and in-order receive acceptance.
- `relhangup` posts a hangup event to the conversation event queue, discards unacked data, resets peer sequence/generation state, and wakes blocked writers.

## Control and Observability
- `headers`: enables Plan 9 UDP-style address headers on read/write.
- `hangup ip port`: forgets a peer and sends a hangup ack.
- `randdrop [percent]`: intentionally drops outgoing packets for testing.
- `rudpstate` reports open/closed state plus per-peer unacked counts.
- `rudpstats` reports datagram counters, retransmits, and out-of-order packets.

## Dependencies and Integration
Uses core Plan 9 IP stack helpers: `Fsstdconnect`, `Fsstdannounce`, `Fsconnected`, `iphtadd`, `iphtlook`, `iphtrem`, `ptclcsum`, `icmpnoconv`, `ipoput4`, queues, `Block` manipulation, `QLock`, `Rendez`, and kernel process timers.

## Risks and Notes
The implementation is IPv4-only despite carrying IPv6-sized internal addresses. Reliability is per-destination inside one conversation, uses a global `generation` counter with wrap avoidance for `Hangupgen`, and assumes in-order delivery to users by rejecting out-of-order data rather than buffering it.
