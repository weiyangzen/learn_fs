# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcp.h

Shared DHCP/BOOTP definitions for IPv4 DHCP programs. Defines lease constants, packet-size constants, BOOTP opcodes/flags, DHCP message types, BOOTP/DHCP option numbers, Plan 9 vendor option numbers, DHCP client states, and `Lforever`.

Defines the packed `Bootp` structure, including Plan 9 `Udphdr`, BOOTP fixed fields, DHCP magic, and option buffer. This header is the common contract for `dhcpclient.c` and `dhcpd`.
