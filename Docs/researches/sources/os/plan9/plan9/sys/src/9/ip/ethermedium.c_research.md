# File Research: sources/os/plan9/plan9/sys/src/9/ip/ethermedium.c

Implements Ethernet and gigabit Ethernet IP media bindings.

Key responsibilities:
- Defines `ethermedium` and `gbemedium` with Ethernet header sizes, MTUs, MAC length, bind/unbind/write, multicast, address-resolution, registration, and IPv6 prefix-to-EUI-64 callbacks.
- `etherbind` opens device conversations for IPv4 (`0x800`), ARP (`0x806`), and IPv6 (`0x86DD`), makes IP channels nonblocking, reads device stats to obtain MAC address and speed, stores channels in `Etherrock`, and starts IPv4, IPv6, and ARP reader kprocs.
- `etherunbind` posts notes to reader processes, waits for shutdown, closes channels, and frees state.
- `etherbwrite` resolves destination MAC via ARP/ND cache, handles broadcast/multicast resolution, sends ARP or neighbor solicitations when unresolved, pads/concats blocks, fills Ethernet headers, and writes to the proper device channel.
- `etherread4` and `etherread6` strip Ethernet headers and hand packets to `ipiput4`/`ipiput6`.
- Implements IPv4 ARP request/reply handling, gratuitous ARP, duplicate address warnings, proxy ARP checks, and ARP cache updates.
- Implements IPv6 address resolution by sending neighbor solicitations.
- Maps IPv4 and IPv6 multicast IP addresses to Ethernet multicast MAC addresses.
- `etherpref2addr` builds an IPv6 interface identifier from a MAC address.

Notable design:
- ARP and IPv6 neighbor discovery integrate with the common ARP cache abstraction.
- Broadcast/multicast destinations bypass ordinary unresolved ARP wait by synthesizing MAC entries.
