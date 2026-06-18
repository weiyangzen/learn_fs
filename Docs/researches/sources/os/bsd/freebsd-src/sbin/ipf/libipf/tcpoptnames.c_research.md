# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcpoptnames.c

TCP option-name table.

Key behavior:
- Defines `tcpoptnames[]` for NOP, MSS, window scale, SACK permitted, SACK, and timestamp.
- Each entry maps TCP option value to bit, expected length, and text name.

Research notes:
- Sentinel row terminates the table.
