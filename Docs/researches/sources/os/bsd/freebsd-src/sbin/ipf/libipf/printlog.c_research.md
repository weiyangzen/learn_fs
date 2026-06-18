# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/printlog.c

Rule logging clause printer.

Key behavior:
- Prints `log` plus `body`, `first`, and `or-block` flags.
- Prints syslog facility/priority names when `fr_loglevel` is set.

Research notes:
- Unknown facility/priority names print as `!!!`.
