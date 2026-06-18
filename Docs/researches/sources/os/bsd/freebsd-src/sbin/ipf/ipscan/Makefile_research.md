# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipscan/Makefile

This FreeBSD makefile builds `ipscan`, the IPFilter content scanner rule tool.

It sets `PACKAGE=ipf`, `PROG=ipscan`, generated parser source `ipscan_y.c`, and manuals `ipscan.5` and `ipscan.8`, with `ipscan.conf.5` as an mlink. `YACC -d` generates both `ipscan_y.c` and `ipscan_y.h`; both are listed in clean files.

The resulting program is primarily generated from `ipscan_y.y`, which embeds both parser and CLI logic.
