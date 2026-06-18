# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpd/testping.c

Tiny test harness for `icmpecho`. It initializes IP formatters, expects an address argument, and reports whether the address answers the DHCP probe.

Useful for checking the probe behavior independently from `dhcpd`.
