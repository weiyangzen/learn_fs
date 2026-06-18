# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/icmptypes.c

This file defines `icmptypelist`, the shared ICMP/ICMPv6 name mapping table.

When IPv6 support is not compiled, it defines missing ICMPv6 constants as zero so the table still compiles. The table maps names such as `echo`, `echorep`, `unreach`, `timex`, router solicitation/advertisement, neighbor solicitation/advertisement, listener/member messages, packet-too-big, FQDN, who, and renumbering to IPv4 and/or IPv6 numeric type values.

This table backs `geticmptype()` and `icmptypename()`.
