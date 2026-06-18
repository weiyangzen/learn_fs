# File Research: sources/os/bsd/openbsd-src/sbin/Makefile

Top-level OpenBSD `sbin` subdirectory makefile.

It enumerates the system administration programs built under `/sbin`, including the files in this group (`atactl`, `badsect`, `bioctl`, `clri`, `dhcp6leased`, and `dhcpleased`) plus filesystem checkers, mount helpers, network daemons, routing tools, and reboot/shutdown utilities. It delegates recursion to `<bsd.subdir.mk>`.
