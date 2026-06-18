# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/44arp.c

This BSD-specific ARP and hostname resolution backend is based on 4.4BSD `/usr/sbin/arp`.

`resolve()` accepts dotted IPv4 strings or hostnames and writes the resolved IPv4 address into a caller-provided 4-byte buffer.

`arp()` uses `sysctl()` over the routing table (`PF_ROUTE`, `NET_RT_FLAGS`, `RTF_LLINFO`) to find a matching IPv4 route/ARP entry and copy its link-layer address from `sockaddr_dl` into the caller-provided Ethernet address buffer. When built for IPSEND, it first attempts `arp_getipv4()` from the IP language support.

Important dependencies include BSD routing/socket headers, `net/if_dl.h`, `netinet/if_ether.h`, `ipsend.h`, and `iplang/iplang.h`.

Implementation notes and risks:
- Allocated route table buffer is not freed on successful lookup or failure.
- Function assumes IPv4 and Ethernet-style link-layer addresses.
- Failure paths may `exit()` on `sysctl()` or allocation errors.
