# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printtcpflags.c

TCP flags/mask formatter.

Key behavior:
- Prints known TCP flags as letters using global `flagset`/`flags`.
- Prints hex for unknown flag bits.
- Appends `/mask` when a mask is supplied.

Research notes:
- Relies on global flag arrays defined elsewhere in libipf.
