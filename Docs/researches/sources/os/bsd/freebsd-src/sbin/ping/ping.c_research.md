# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping.c

## Purpose
IPv4 ICMP ping implementation: raw socket setup, option parsing, packet generation, receive loop, reply validation, and output.

## Main Elements
- Defines IPv4-specific option flags, duplicate tracking bitmap, sockets, packet buffers, ICMP types, payload sizes, counters, sweep settings, and Casper DNS channel.
- `ping()` opens raw ICMP send/receive sockets before dropping setuid privileges, parses IPv4 options, resolves source/target via Casper DNS, configures socket options, enters Capsicum/Casper capability mode, sends initial/preload packets, and runs the receive/transmit loop.
- Supports flood, interval, count, timeout, waittime, payload pattern, sweep sizes, TTL, TOS, VLAN PCP, multicast options, record route, IP_HDRINCL/DF, mask request, timestamp request, audible/dot/quiet modes, source bind, and IPsec policy.
- `pinger()` constructs ICMP packets, embeds monotonic timestamps, computes ICMP/IP checksums, sends packets, and updates counters.
- `pr_pack()` validates received IP/ICMP lengths, matches replies to process ID, computes RTT, tracks duplicates, validates returned data, handles ICMP errors with quoted-packet checks, prints IP options, and updates stats.
- `pr_icmph()`, `pr_iph()`, `pr_addr()`, and `pr_ntime()` format ICMP/IP diagnostics, addresses, and timestamps.
- `fill()` parses hexadecimal payload patterns.
- `capdns_setup()` opens and limits Casper DNS service.

## Dependencies And Integration
Uses raw IPv4 sockets, Capsicum/Casper, IPsec conditionals, `in_cksum()` from `utils.c`, and shared globals/functions from `main.h`.

## Risk Notes
Security-sensitive due to setuid-root raw socket creation and later capability reduction. Packet parsing uses defensive length checks to avoid malformed ICMP/IP data. Exact output is test-sensitive.
