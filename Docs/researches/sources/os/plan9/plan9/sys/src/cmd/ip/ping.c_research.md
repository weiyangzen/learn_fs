# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ping.c

IPv4/IPv6 ICMP echo client with RTT tracking, protocol autodetection, optional address display, randomized intervals, and loss reporting.

Key behavior:
- `Proto` abstracts IPv4 vs IPv6 ICMP command/reply types, IP header sizes, and output formatting.
- `isv4name` parses dial strings and consults connection server lookups to choose IPv4 or IPv6 unless `-6` forces IPv6.
- `sender` constructs ICMP echo packets, chooses a non-loopback local source address via `myipvnaddr`, stores outstanding `Req` nodes, and writes packets.
- `rcvr` reads replies, validates length/type/code/sequence and payload pattern, computes RTT, and calls `clean`.
- `clean` matches replies to outstanding requests and marks old requests lost after one minute.
- `reply` and `lost` update counters and print per-message output unless quiet/lost-only options suppress it.
- Options include message size, interval, count, quiet, flood, lost-only, randomized interval, wait timeout, and address printing.

Integration points:
- Uses Plan 9 `/net/icmp` and `/net/icmpv6` via `dial`, `readipifc`, `csgetvalue`, and `%I`/`%V` formatting.

Risks and notes:
- `rcvr` checks `n < msglen`, so IP stacks returning shorter-than-requested echo replies are reported as bad length.
- Source address selection deprecates link-local/multicast and falls back to link-local only if no global address exists.
