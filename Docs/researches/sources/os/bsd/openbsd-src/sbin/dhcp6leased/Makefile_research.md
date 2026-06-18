# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/Makefile

Build recipe for the DHCPv6 prefix-delegation daemon.

It builds `dhcp6leased` from the control, main, engine, frontend, logging, configuration parser, lease parser, and print-config sources. It installs `dhcp6leased.8` and `dhcp6leased.conf.5`, enables strict warning flags, links against `libevent` and `libutil`, generates `parse_lease.c` with a `pl` yacc prefix, and explicitly disables static linking for this daemon.
