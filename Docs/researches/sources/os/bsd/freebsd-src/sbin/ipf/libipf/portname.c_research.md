# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/portname.c

Port-number to service-name formatter.

Key behavior:
- Honors `OPT_NORESOLVE`.
- With protocol `-1`, tries to return a name common to TCP and UDP.
- With a concrete protocol, resolves through `getprotobynumber()` then `getservbyport()`.
- Falls back to decimal text.

Research notes:
- Returns a static buffer.
