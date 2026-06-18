# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ping.c

IPv4/IPv6 ping implementation. It chooses ICMP or ICMPv6, sends echo requests with sequence numbers and patterned payload data, records send times in a locked request list, and receives replies in a forked process.

It reports RTT, average RTT, TTL, optional source/destination addresses, corrupted replies, lost messages, and final loss count. Options control IPv6, address printing, quiet/lost-only modes, interval, randomized interval, flood mode, message count, size, and wait timeout.
