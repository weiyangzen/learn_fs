# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/Makefile

Build recipe for the IPv4 DHCP lease daemon.

It builds `dhcpleased` from BPF, checksum, control, main, engine, frontend, logging, parser, and print-config sources. It installs `dhcpleased.8` and `dhcpleased.conf.5`, enables strict warning flags, links against `libevent` and `libutil`, and disables static linking by default.
