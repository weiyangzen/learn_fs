# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/Makefile

This Makefile builds the FreeBSD `ifconfig` utility and controls which address-family and feature modules are compiled based on `src.opts.mk` knobs.

It always includes the base dispatcher plus link, clone, MAC, media, FIB, VLAN, VXLAN, GRE, GIF, IPsec, SFP, CARP, group, bridge, and lagg support. IPv4, IPv6, ND6/STF, wireless, pfsync, jail, and netlink/GENEVE pieces are conditional. The comments note that source order defines constructor order and therefore default status display order.

It links against `libifconfig`, `libm`, `libutil`, `libnv`, optional `lib80211`, and optional `libjail`, installs `ifconfig.8`, enables warning flags, and includes tests when requested.
