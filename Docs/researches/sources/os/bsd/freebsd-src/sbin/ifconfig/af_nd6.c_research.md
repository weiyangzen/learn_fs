# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_nd6.c

`af_nd6.c` provides IPv6 Neighbor Discovery option handling used by the IPv6 module. It gets/sets ND6 interface flags with `SIOCGIFINFO_IN6` and `SIOCSIFINFO_IN6`, and manages the default IPv6 interface with `SIOCGDEFIFACE_IN6`/`SIOCSDEFIFACE_IN6`.

`nd6_status()` opens an IPv6 datagram socket, reads ND6 flags, checks whether the interface is the default interface, and prints `nd6 options=` only when options or default-interface state are present. The bit-name table covers NUD, router-advertisement, source preference, disabled, route suppression, auto-linklocal, RADR, DAD, stable-address, and default-interface state.
