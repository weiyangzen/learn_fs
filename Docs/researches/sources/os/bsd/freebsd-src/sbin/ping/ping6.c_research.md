# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping6.c

FreeBSD `ping6` implementation for IPv6 ICMP echo and IPv6 Node Information queries.

Key elements:
- `ping6(int argc, char *argv[])` parses IPv6 ping options, resolves target/source/gateway addresses through Casper DNS, opens raw ICMPv6 send/receive sockets, configures socket options, drops privilege, enters Capsicum capability mode, sends probes, receives replies with `recvmsg`, and exits with ping-compatible status.
- Supports echo request/reply, flood mode, quiet mode, audible/missed-packet indicators, source address/interface selection, hop limit, traffic class, VLAN PCP, no-fragment, wait timeout, preload, route headers, minimum MTU/path MTU options, and optional IPsec policy handling.
- Node Information modes include FQDN, old FQDN draft format, node address, supported query types, and multicast NI group address generation via MD5 in `nigroup`.
- `pingerlen` and `pinger` compose either ICMPv6 echo requests or ICMPv6 NI queries. Echo timing stores a compact 32-bit seconds/nanoseconds timestamp in the payload.
- `pr_pack` validates received sockaddr/control data, extracts hop limit and packet info, recognizes this process’s echo or NI replies, updates packet counters/timing stats, detects duplicates through `rcvd_tbl`, checks returned payload bytes, and prints normal or verbose output.
- Packet printers cover extension headers, hop-by-hop/destination options, routing headers, supported NI qtype bitmaps, NI node addresses, ICMPv6 error classes, returned IPv6 headers, TCP/UDP quoted ports, and DNS name decoding.
- `capdns_setup` opens `system.dns` through Casper and limits DNS operations to IPv6 name/address lookups when built with Casper support.

Dependencies:
- Shares global ping state and helpers from `main.h`, including `options`, `hostname`, counters, timing accumulators, signal flags, `usage`, `onsignal`, and `pr_summary`.
- Uses FreeBSD-specific Capsicum/Casper APIs, raw IPv6 socket options, ICMPv6/Node Information definitions, routing header helpers, and optional IPsec APIs.
- Uses `<md5.h>` for NI multicast group generation.

Research notes:
- The program does privileged setup first, then drops uid/euid and further restricts descriptors under Capsicum; later DNS is limited to reverse lookups.
- Receive-side validation depends on `IPV6_HOPLIMIT` and `IPV6_PKTINFO` control messages being delivered; missing ancillary data makes a packet unusable.
- `setpolicy(int so __unused, char *policy)` ignores its `so` argument and applies policy to the global send socket.
- Exit codes distinguish at least one reply (`0`), transmitted but no replies (`2`), and send/open/system failure (`EX_OSERR` or `err` path).
