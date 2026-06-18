# File Research: sources/os/bsd/openbsd-src/sbin/unwind/frontend.c

Main frontend process for OpenBSD `unwind`. It owns client-facing UDP/TCP DNS sockets, validates and logs queries, relays query requests to the resolver process over imsg, receives streamed answers, rewrites or synthesizes replies, tracks network changes, handles trust anchors, and enforces a domain blocklist.

Major responsibilities:
- Starts chrooted under `UNWIND_USER`, drops privileges, and pledges `stdio dns unix recvfd`.
- Receives socket file descriptors and configuration over imsg from the main process.
- Maintains UDP and TCP pending query state in `struct pending_query`.
- Parses DNS queries with Unbound/sldns helpers, validates header semantics, EDNS, qname, qtype, and qclass.
- Rejects AXFR/IXFR and malformed meta/obsolete types.
- Answers CHAOS `version.server.` and `version.bind.` locally with `unwind`.
- Relays accepted queries to resolver via `IMSG_QUERY`.
- Receives resolver answers in chunks using `answer_header->answer_len` and assembles them into `pq->abuf`.
- Re-encodes successful replies through Unbound `reply_info_parse()` / `reply_info_encode()` to preserve frontend policy and answer minimization.
- Performs DNS64 retry/synthesis for AAAA queries when no AAAA answer is present and DNS64 prefixes are configured.
- Handles route socket messages to notify resolver about network/DNS changes.
- Tracks available IPv4/IPv6 address families using `getifaddrs()` and sends `IMSG_CHANGE_AFS`.
- Parses, sorts, merges, sends, and writes trust anchors.
- Parses blocklist files into a reversed-domain RB tree supporting exact and wildcard-ish suffix comparison.
- Implements TCP accept backoff on descriptor exhaustion and per-query TCP timeout.

DNS64 flow:
- `noerror_answer()` parses a normal resolver answer. If it is an IN AAAA query, no answer rrset is present, and `dns64_prefix_count > 0`, it sets `pq->dns64_synthesize`.
- Resolver dispatch then calls `resend_dns64_query()`, which clones query state, changes the resolver query type to A, and marks the new pending query for synthesis.
- On the A answer, `synthesize_dns64_answer()` creates a new `reply_info`, converts answer-section A rrsets to AAAA via `dns64_synth_aaaa_data()`, copies other rrsets, and re-encodes the original AAAA response.

Networking:
- UDP uses `recvmsg()` into static `udp_ev` buffers and `sendto()` for replies.
- TCP accepts nonblocking sockets with `accept4()`, reads a two-byte DNS length prefix, then writes a length-prefixed response.
- `accept_reserve()` keeps `FD_RESERVE` descriptors free.

Route handling:
- `RTM_PROPOSAL` with `RTA_DNS` sends `IMSG_REPLACE_DNS`.
- `RTM_IFINFO` sends `IMSG_NETWORK_CHANGED`.
- address/desync events trigger address-family availability checks.
- interface removal sends a replacement DNS proposal with empty `sockaddr_rtdns`.

Security posture:
- Strong OpenBSD privilege separation: chroot, uid/gid drop, pledge, fd passing.
- Query validation happens before resolver relay.
- Resolver answers that are bogus and not client-CD are converted to SERVFAIL.
- Blocklist returns REFUSED.
