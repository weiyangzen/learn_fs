# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sockio.h

## Role

Defines socket, routing, ARP, interface, logical-interface, multicast, SCTP, PF_PACKET, and private networking ioctl command numbers.

## Key Contents

Includes classic socket ioctls for watermarks, OOB mark, and process group. Defines route ioctls, multicast routing counters, obsolete `struct ifreq` interface controls, newer `struct lifreq` IPv4/IPv6 logical-interface controls, address query ioctls, IPMP controls, IPv6 address policy controls, extended ARP controls, sockfs fallback ioctl, zone-interface association controls, SCTP option/peeloff ioctls, source address controls, RFC 3678 source-filter controls, PF_PACKET hardware-address/timestamp controls, ILB ioctl, module property ioctls, DAD state, IPv6 prefix generation, and logical-interface hardware address query.

## Design Notes

Many commands use `_IOWRN` or `_IOWN` to remain data-model independent. The file preserves extensive historical ioctl numbering and marks reusable gaps left by removed private interfaces.
