# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypename.c

This helper maps a numeric ICMP type to a shared name for a given address family.

It rejects values outside `0..255`, scans `icmptypelist`, and returns the first name whose IPv4 or IPv6 type matches. Unknown types return `NULL`.
