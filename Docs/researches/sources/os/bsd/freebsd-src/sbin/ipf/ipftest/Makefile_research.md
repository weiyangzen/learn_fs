# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/Makefile

This Makefile builds the `ipftest` program in the FreeBSD IPFilter userland tree.

Key points:
- `PROG=ipftest`, `PACKAGE=ipf`, manual page `ipftest.1`.
- Sources combine local test harness files (`ipftest.c`, `ip_fil.c`, `md5.c`) with many kernel IPFilter implementation files from `${SRCTOP}/sys/netpfil/ipfilter/netinet`.
- Enables `IPFILTER_LOG`, `IPFILTER_COMPILED`, `IPFILTER_LOOKUP`, `IPFILTER_SYNC`, `IPFILTER_CKSUM`, and `HAS_SYS_MD5_H`.
- Explicitly does not enable `IPFILTER_SCAN`; comments say the original tarball did not define it and it is believed to fail building.
- Generates renamed parser/lexer files for IPF, IPNAT, and IPPOOL grammars by running yacc and sed-rewriting `yy` prefixes to `ipf_yy`, `ipnat_yy`, and `ippool_yy`.

The build design lets `ipftest` link large portions of the kernel packet filter/NAT/state/lookup code into a user-space executable.
