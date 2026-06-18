# File Research: sources/os/bsd/openbsd-src/sbin/ping/ping.c

## Purpose

Combined IPv4/IPv6 `ping` implementation. It sends ICMP Echo requests on raw sockets, receives replies and diagnostic ICMP messages, prints per-packet output, tracks duplicates and RTT statistics, and supports legacy IPv4 options plus IPv6 control-message diagnostics.

## Program Setup

The binary chooses IPv6 mode when invoked as `ping6`; otherwise it uses IPv4. It opens the raw ICMP socket before dropping privileges. If initially run as root and `_ping` exists, it later drops to that user and group; otherwise it drops to the real uid/gid. Options configure count, don't-fragment/header inclusion, socket debug, audible notifications, flood mode, show-character mode, hostname resolution, hoplimit/TTL, source address, interval, preload, multicast loop/TTL/min-MTU behavior, payload pattern and size, quiet/verbose mode, record-route, TOS/traffic class, routing table, and max wait.

The program unveils `/` read-only early because name and service resolution may need filesystem access, then pledges to `stdio inet` or `stdio inet dns` after socket setup depending on whether hostname lookup output is enabled.

## Packet Sending

`pinger()` constructs an ICMP or ICMPv6 Echo Request with a random 16-bit identifier and incrementing sequence number. When the payload is large enough, it writes a timing payload containing a monotonic timestamp with a random offset and a SipHash MAC over timestamp, identifier, and sequence. IPv4 computes the ICMP checksum, and when `IP_HDRINCL` is used it also fills the IP header and checksum. Packets are sent with `sendmsg()` using a shared `msghdr`; IPv6 hoplimit can be supplied as a control message.

## Receive Loop

Startup drains pending packets from the raw socket under a one-second timer. Normal operation uses signals as flags: SIGALRM triggers retransmit, SIGINT exits, and SIGINFO prints an interim summary. Non-flood mode uses an interval timer; flood mode sends aggressively until count is exhausted and then waits for late replies. The loop uses `poll()` and `recvmsg()` with room for ancillary data. Zero-length IPv6 reads are treated as control-message notifications, currently path MTU updates.

## Packet Parsing And Statistics

`pr_pack()` validates peer address family and minimum lengths, parses IPv4 IP headers or raw ICMPv6 headers, filters echo replies by identifier, obtains IPv6 hoplimit from control messages, and handles non-echo ICMP output only in verbose mode. Valid echo replies increment `nreceived`; duplicate detection uses a bitset indexed by sequence modulo `MAX_DUP_CHK`.

RTT calculation is accepted only if the SipHash MAC in the returned payload matches. This prevents unrelated, stale, or forged payload bytes from feeding timing statistics. Timing values update min, max, sum, and sum-of-squares for standard deviation. Printed output includes bytes, source address, sequence, TTL/hoplimit, RTT, duplicate/truncation flags, and optional payload mismatch dumps.

## Diagnostic Printers

IPv4 helpers include `pr_ipopt()`, `in_cksum()`, `pr_icmph()`, `pr_iph()`, and `pr_retip()`. They print record-route/LSRR options, ICMP unreachable/redirect/time-exceeded/parameter/timestamp/router/mask messages, returned IP headers, and TCP/UDP ports in embedded packets.

IPv6 helpers include `pr_exthdrs()`, `pr_ip6opt()`, `pr_rthdr()`, `get_hoplim()`, `get_pathmtu()`, `pr_icmph6()`, `pr_iph6()`, and `pr_retip6()`. They print extension headers, hop-by-hop/destination options, routing headers, path MTU notifications, ICMPv6 error/ND messages, and embedded IPv6 packet chains.

## Risks And Invariants

- Raw sockets are opened before privilege drop; later privileged socket options must be set before pledge.
- Non-root users cannot use flood mode, preload, or subsecond intervals.
- Duplicate tracking is modulo a fixed bitset; very long runs can alias old sequence numbers.
- The timing payload requires `datalen >= sizeof(struct payload)`.
- Several diagnostic routines intentionally parse packet bytes from the network; they do length checks in key paths, but older printer code assumes embedded protocol headers are present once reached.
