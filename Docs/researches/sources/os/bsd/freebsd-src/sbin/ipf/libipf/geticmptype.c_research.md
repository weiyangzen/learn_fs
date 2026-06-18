# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/geticmptype.c

This helper maps an ICMP type name to the numeric type for a given address family.

It scans `icmptypelist`, compares by name, returns the IPv4 or IPv6 type field for `AF_INET`/`AF_INET6`, and returns `-1` for unsupported family or unknown name.
