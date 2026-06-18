# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/main.c

Main `ipconfig` command. It parses media, device, verbs, IPv4/IPv6 addresses, DHCP flags, ndb configuration, route options, MTU, DNS, DUID, and control messages; binds or reuses an IP interface; then dispatches add, delete, unbind, IPv6 prefix, or RA actions.

IPv4/IPv6 add paths configure addresses, default routes, proxy/translation flags, DHCP or static settings, and refresh `/net/cs` and `/net/dns`. DHCP-learned and ndb-learned data is written into `/net/ndb` with duplicate filtering and checksum-based rewrite suppression.

The file also owns route-control formatting, primary/non-primary behavior, ndb lookups by Ethernet/IP, address/name packing helpers, warning/debug output, random jitter, interface discovery, and cleanup/removal paths.
