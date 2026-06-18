# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/af_inet6.c

`af_inet6.c` implements IPv6 support for `ifconfig`, including address parsing, prefix handling, address flags, lifetimes, EUI-64 suffix filling, ND6 command registration, tunnel setup/display, and CARP VHID propagation.

Status output prints IPv6 address, point-to-point destination, prefix length, IPv6 address flags, scope ID, optional preferred/valid lifetime, and VHID. Commands include `prefixlen`, anycast/tentative/deprecated/autoconf/prefer_source, ND6 toggles, `pltime`, `vltime`, `eui64`, and the `-L` option for lifetime display.

The file supports both ioctl and netlink builds. Ioctl mode uses `in6_aliasreq`, `in6_ifreq`, `SIOCAIFADDR_IN6`, `SIOCDIFADDR_IN6`, and `SIOCSIFPHYADDR_IN6`; netlink mode builds IPv6 address messages with `IFA_LOCAL`, optional peer address, cacheinfo lifetime, FreeBSD flags, and VHID. If no prefix is explicit, post-processing defaults IPv6 prefixes to 64.
