# File Research: sources/os/plan9/9front/sys/src/cmd/ip/linklocal.c

Utility that prints an IPv6 link-local address, or a 6to4 address with `-t ipv4`, for each Ethernet MAC address argument. It converts MAC-48 to EUI-64 by inserting `ff:fe` and toggling the universal/local bit, then formats either `fe80::/64` or `2002:<ipv4>::/48`-derived addresses.
