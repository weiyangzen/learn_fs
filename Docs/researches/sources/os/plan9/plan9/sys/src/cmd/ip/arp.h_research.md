# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/arp.h

`arp.h` defines shared ARP/RARP packet and cache structures.

Key contents:
- `Arppkt` maps Ethernet ARP packet layout.
- `ARPSIZE` is defined as 42.
- `Arpentry` maps an Ethernet address to IPv4 address for user-level ARP interactions.
- `Arpstats` tracks hits, misses, and failed lookups.
- Defines EtherType and ARP/RARP operation constants.

Important dependencies:
- Comment notes use by kernel, arpd, snoopy, and tboot.

Notable risks/quirks:
- IPv4/Ethernet-specific fixed layout.
