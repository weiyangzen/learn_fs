# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipresend/Makefile

This FreeBSD makefile builds the `ipresend` program from source files located in the sibling `ipsend` directory via `.PATH`.

It sets `PACKAGE=ipf`, `PROG=ipresend`, source files `ipresend.c ip.c resend.c sbpf.c sock.c 44arp.c`, and installs the `ipresend.1` manual page. It includes `<bsd.prog.mk>` for normal FreeBSD program build rules.

The selected source set targets a BPF/BSD backend.
