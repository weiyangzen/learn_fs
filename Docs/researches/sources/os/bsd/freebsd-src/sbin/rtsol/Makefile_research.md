# File Research: sources/os/bsd/freebsd-src/sbin/rtsol/Makefile

## Summary
Builds the `rtsol` runtime utility from sources shared with `usr.sbin/rtsold`.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/usr.sbin/rtsold`.
- Builds `PROG=rtsol` with no installed man page from this Makefile.
- Reuses `cap_llflags.c`, `cap_script.c`, `cap_sendmsg.c`, `dump.c`, `if.c`, `rtsol.c`, `rtsold.c`, and `rtsock.c`.
- Links `libutil`.
- Conditionally enables Casper support unless dynamic root is disabled, Casper is disabled, or building rescue.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`, `src.opts.mk`, and optional `cap_syslog`, `casper`, and `nv` libraries.
