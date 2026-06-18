# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/arp.c

This is another ARP/resolve backend for `ipsend`, using `SIOCGARP` rather than routing-table `sysctl()`.

`resolve()` mirrors the IPv4 dotted/hostname resolver in `44arp.c`.

`arp()` caches the last IP-to-Ethernet mapping, optionally delegates to `arp_getipv4()` under `IPSEND`, tries `/etc/ethers` style lookup through `ether_hostton()`, then uses an AF_INET datagram socket and `SIOCGARP`. If an ARP entry is missing, it sends a small UDP datagram to stimulate ARP resolution, sleeps, and retries once.

Important dependencies include `sys/sockio.h`, `net/if_arp.h`, `netinet/if_ether.h`, `ipsend.h`, and `iplang/iplang.h`.

Implementation notes and risks:
- IPv4-only, Ethernet-specific.
- Uses static cache and static socket, so it is not thread-safe.
- ARP probing has blocking `sleep(1)` behavior.
- Some errors return `-1`; socket creation errors are printed directly.
