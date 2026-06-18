# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/tcp_flags.c

TCP flags plus mask parser.

Key behavior:
- Parses `flags` or `flags/mask`, accepting symbolic letters or numeric values starting with `0`.
- Defaults mask to all TCP flags except ECN, and also except CWR for bare SYN.
- Returns parsed flags and writes parsed/default mask.

Research notes:
- `linenum` parameter is unused.
