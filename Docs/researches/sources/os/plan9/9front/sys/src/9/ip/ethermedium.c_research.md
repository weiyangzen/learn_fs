# File Research: sources/os/plan9/9front/sys/src/9/ip/ethermedium.c

Implements the Ethernet and gigabit-Ethernet `Medium` adapters for the IP stack. It binds `Ipifc` interfaces to Ethernet device conversations, sends IPv4/IPv6 frames, receives frames into the IP stack, and handles ARP/NDP media behavior.

Key responsibilities:
- Registers `ethermedium` and `gbemedium`.
- Binds an IP interface to an Ethernet device in `etherbind()`.
- Opens three Ethernet conversations: IPv4 ethertype `0x800`, IPv6 ethertype `0x86DD`, and ARP ethertype `0x806`.
- Runs reader processes for IPv4, IPv6, and ARP.
- Performs Ethernet header construction and ARP/NDP resolution in `etherbwrite()`.
- Manages multicast MAC subscription commands.
- Sends ARP requests, gratuitous ARP, IPv6 neighbor solicitations/advertisements, and duplicate address detection probes.

Important implementation details:
- `Etherrock` stores channels and reader process identities for one bound interface.
- `etherunbind()` posts notes to reader processes, waits for exit, closes channels, and frees the medium state.
- `multicastarp()` resolves broadcast and multicast destinations without issuing ARP/NDP queries.
- IPv4 multicast maps to `01:00:5e:...`; IPv6 multicast maps to `33:33:...`.
- `etherpref2addr()` builds an IPv6 EUI-64 address suffix from a MAC address.
- `etherareg()` sends gratuitous ARP for IPv4 and performs IPv6 neighbor advertisement or DAD behavior for IPv6.

Dependencies and integration:
- Uses `chandial()` to access Ethernet device channels.
- Uses ARP cache APIs: `arpget`, `arpcontinue`, `arpresolve`, `arpenter`, `arpforme`.
- Delivers inbound payloads to `ipiput4()` and `ipiput6()`.
- Uses ICMPv6 helpers `icmpns6()` and `icmpna6()`.

Research notes:
- This file is the concrete media bridge from IP packets to Ethernet frames.
- `gbemedium` differs mainly by MTU: 9000-byte max payload plus Ethernet header.
- Unbind logic is careful because reader processes may initiate unbind after device errors.
