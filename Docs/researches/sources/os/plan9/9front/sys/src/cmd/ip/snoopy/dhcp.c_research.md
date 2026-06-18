# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/dhcp.c

This module prints DHCP option data after BOOTP has positioned the message cursor at the option stream. It has no compile/filter hooks and is print-only.

Helper printers format byte arrays as hex, strings, signed/unsigned integers, IPv4 server lists, classful routes, and classless routes. `dhcptype` maps DHCP message type option values to names.

`p_seprint` walks TLV options until end option 255, skipping pad option 0 and stopping on malformed overrun. It recognizes common DHCP and BOOTP option constants from `../dhcp.h`: requested address, lease, message type, server id, message text, max message size, client id, parameter request list, vendor class, subnet mask, router, DNS, hostname, domain, MTU, static routes, classless routes, NetBIOS options, NTP, SMTP, POP3, WWW, IRC, and many others. Unknown options are printed as hex under `T<number>`.

The module terminates traversal with no next protocol.
