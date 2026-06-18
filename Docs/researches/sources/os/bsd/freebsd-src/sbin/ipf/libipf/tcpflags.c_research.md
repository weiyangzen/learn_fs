# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpflags.c

Symbolic TCP flag-string converter.

Key behavior:
- Converts characters from global `flagset` into TCP flag bits from global `flags`.
- Handles `W` explicitly as `TH_CWR`.
- Provides fallback definitions for ECN, CWR, and AE flag constants.

Research notes:
- Unknown flag characters make the whole conversion return zero.
