# File Research: sources/os/bsd/freebsd-src/sbin/ping/main.c

## Purpose
Protocol dispatcher and shared summary/signal handling for `ping`.

## Main Elements
- Defines shared option, hostname, packet counters, signal flags, and timing accumulators.
- Dispatches to `ping6()` when invoked as `ping6`.
- Scans early options to force IPv4/IPv6 on `-4`, `-6`, or numeric `-S`.
- Resolves target with `getaddrinfo()` when both INET and INET6 are compiled, choosing IPv4 or IPv6 based on result and available kernel features.
- Resets getopt state before calling protocol-specific implementation.
- `onsignal()` records SIGINT/SIGALRM/SIGINFO and exits on second SIGINT when safe.
- `pr_summary()` prints packet loss and round-trip min/avg/max/stddev.
- `usage()` prints IPv4 and IPv6 usage forms according to compile-time options.

## Dependencies And Integration
Includes `ping.h` and `ping6.h` conditionally. Shared globals are declared in `main.h` and used by protocol implementations.

## Risk Notes
Dispatcher resolution loses IPv6 intermediate-hop nuance except for final error handling. Signal behavior must stay async-safe.
