# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ethernet.h

## Role

`ethernet.h` provides common Ethernet address, header, EtherType, frame-size, comparison/copy, and address conversion declarations used by kernel and userland.

## Packet And Address Structures

- Defines `ETHERADDRL`, `ETHERFCSL`, and `ETHERADDRSTRL`.
- Defines `ether_addr_t`, `struct ether_addr`, `struct ether_header`, `struct ether_vlan_header`, and `struct ether_vlan_extinfo`.
- Defines VLAN CFI and common EtherTypes: PUP, IP, ARP, REVARP, AppleTalk/AARP, VLAN, IPv6, slow protocols, PPPoE, EAPOL, RSN preauth, TRILL, FCoE, and max type.
- Defines trailer packet type range, MTU/min/max frame size constants.

## Helpers And APIs

- `ether_cmp()` and `ether_copy()` use short-sized loads/stores on SPARC/x86/x64 and fall back to `bcmp()`/`bcopy()` elsewhere.
- Kernel declarations include `ETHER_IS_MULTICAST()`, `localetheraddr()`, `ether_sprintf()`, and kernel `ether_aton()`.
- Userland declarations include `ether_ntoa()`, `ether_ntoa_r()`, `ether_aton()`, `ether_aton_r()`, `ether_ntohost()`, `ether_hostton()`, and `ether_line()`.
