# File Research: sources/os/bsd/freebsd-src/sbin/ping/ping6.h

Small public header for the IPv6 ping entry point.

Key elements:
- Include guard `PING6_H`.
- Declares `int ping6(int argc, char *argv[]);`.

Dependencies:
- Consumed by the ping main program and implemented in `ping6.c`.

Research notes:
- No structs, macros, or shared state are exposed; the header intentionally keeps IPv6 ping integration to one function.
