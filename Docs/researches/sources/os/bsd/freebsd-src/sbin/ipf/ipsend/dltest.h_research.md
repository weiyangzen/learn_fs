# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dltest.h

This header defines constants and macros used by the DLPI helper/test code.

It sets maximum DLPI control/data buffer size (`MAXDLBUF`), acknowledgement timeout seconds (`MAXWAIT`), maximum address buffer length (`MAXDLADDR`), and the `OFFADDR()` pointer arithmetic macro for accessing variable-length data behind DLPI structures.

It declares `sigalrm()` and is intended for the legacy `dlcommon.c`/DLPI backend code.
