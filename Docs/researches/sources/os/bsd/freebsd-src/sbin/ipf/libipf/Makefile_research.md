# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/Makefile

This FreeBSD makefile builds the internal `libipf` library.

It sets `PACKAGE=ipf`, `LIB=ipf`, `INTERNALLIB=`, and enumerates a large collection of shared IPFilter userland helper sources: parsing, rule printing, lookup loading/removal, kernel memory helpers, packet formatting, NAT/state formatting, option handling, variable expansion, logging, and compatibility shims.

It links with `LIBADD=kvm`, reflecting helpers that inspect kernel memory.

The files in this group are the early portion of this shared helper library.
